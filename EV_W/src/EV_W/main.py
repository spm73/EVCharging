import os
import sys
import time
import threading
import requests

# ==========================================
# ESTADO GLOBAL COMPARTIDO
# ==========================================
# Diccionario para mapear CPs a ciudades y recordar su último estado
# Formato: {"CP-01": {"city": "Madrid", "is_frozen": False}}
cp_locations = {}

# Candado (Lock) para evitar que el menú y el demonio modifiquen el 
# diccionario a la vez y corrompan la memoria
state_lock = threading.Lock()

# ==========================================
# FUNCIONES DE RED
# ==========================================
def get_temperature(city: str, api_key: str) -> float | None:
    """Consulta la API de OpenWeather para obtener la temperatura en Celsius."""
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        return float(data["main"]["temp"])
    except requests.RequestException as e:
        print(f"\n[!] Error fetching weather for {city}: {e}")
        return None
    except KeyError:
        print(f"\n[!] Invalid response format for {city}. Is the city name correct?")
        return None

def notify_central(cp_id: str, is_frozen: bool, temperature: float, base_url: str) -> bool:
    """Sends weather alerts to EV_Central's API."""
    url = f"{base_url}/api/cps/{cp_id}/weather-alert"
    try:
        if is_frozen:
            response = requests.post(url, json={"temperature": temperature}, timeout=5)
        else:
            response = requests.delete(url, json={"temperature": temperature}, timeout=5)
            
        response.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"\n[!] Failed to notify EV_Central for {cp_id}: {e}")
        return False

# ==========================================
# DEMONIO METEOROLÓGICO (SEGUNDO PLANO)
# ==========================================
def weather_daemon(api_key: str, central_url: str):
    """Bucle infinito que comprueba las temperaturas cada 4 segundos."""
    while True:
        # Bloqueamos el estado solo un milisegundo para copiar los datos actuales
        with state_lock:
            current_mappings = list(cp_locations.items())

        for cp_id, info in current_mappings:
            temp = get_temperature(info["city"], api_key)
            
            if temp is None:
                continue

            # Actualizar temperatura en la Central en cada ciclo (independientemente de las alertas)
            try:
                requests.patch(f"{central_url}/api/cps/{cp_id}/temperature", json={"temperature": temp}, timeout=2)
            except requests.RequestException:
                pass

            # Determinamos si hace bajo cero
            is_currently_frozen = temp < 0.0

            # 1. Transición de Normal a Congelado
            if is_currently_frozen and not info["is_frozen"]:
                print(f"\n[*] ALERT: {info['city']} dropped to {temp}ºC. Notifying Central to STOP {cp_id}...")
                if notify_central(cp_id, True, temp, central_url):
                    with state_lock:
                        cp_locations[cp_id]["is_frozen"] = True

            # 2. Transición de Congelado a Normal
            elif not is_currently_frozen and info["is_frozen"]:
                print(f"\n[*] INFO: {info['city']} recovered to {temp}ºC. Notifying Central to RESUME {cp_id}...")
                if notify_central(cp_id, False, temp, central_url):
                    with state_lock:
                        cp_locations[cp_id]["is_frozen"] = False
                        
        # Requisito estricto: esperar 4 segundos entre rondas
        time.sleep(4)

# ==========================================
# MENÚ INTERACTIVO (HILO PRINCIPAL)
# ==========================================
def interactive_menu():
    """Menú CLI que permite al profesor inyectar cambios en caliente."""
    print("========================================")
    print("   EV_Weather (Weather Control Office)  ")
    print("========================================")
    
    while True:
        print("\nOptions:")
        print("1. Map a CP to a City")
        print("2. Remove a CP mapping")
        print("3. List current mappings")
        print("q. Quit")
        
        choice = input("\nSelect option: ").strip().lower()
        
        if choice == '1':
            cp_id = input("Enter CP ID (e.g., CP-01): ").strip()
            city = input("Enter City Name (e.g., Madrid): ").strip()
            
            if cp_id and city:
                with state_lock:
                    # Si ya existía, conservamos su estado de congelación para no romper la lógica
                    current_frozen_state = cp_locations.get(cp_id, {}).get("is_frozen", False)
                    cp_locations[cp_id] = {"city": city, "is_frozen": current_frozen_state}
                print(f"[+] Successfully mapped {cp_id} to {city}.")
                
        elif choice == '2':
            cp_id = input("Enter CP ID to remove: ").strip()
            with state_lock:
                if cp_id in cp_locations:
                    del cp_locations[cp_id]
                    print(f"[-] Removed mapping for {cp_id}.")
                else:
                    print(f"[!] {cp_id} not found.")
                    
        elif choice == '3':
            with state_lock:
                if not cp_locations:
                    print("[-] No active mappings.")
                else:
                    print("\n--- Current Mappings ---")
                    for c_id, info in cp_locations.items():
                        state = "FROZEN" if info['is_frozen'] else "NORMAL"
                        print(f" - {c_id} -> {info['city']} [State: {state}]")
                    print("------------------------")
                    
        elif choice == 'q':
            print("Shutting down EV_Weather...")
            sys.exit(0)
            
        else:
            print("[!] Invalid option.")

# ==========================================
# INICIO DE LA APLICACIÓN
# ==========================================
def main():
    api_key = os.getenv("OPENWEATHER_API_KEY")
    central_url = os.getenv("CENTRAL_API_URL")

    if not api_key or not central_url:
        print("[!] Critical Error: OPENWEATHER_API_KEY and CENTRAL_API_URL must be provided.")
        sys.exit(1)

    # Iniciar el hilo del demonio en modo "daemon=True" 
    # Esto asegura que si el menú principal se cierra, este hilo secundario también muere.
    daemon_thread = threading.Thread(
        target=weather_daemon, 
        args=(api_key, central_url), 
        daemon=True
    )
    daemon_thread.start()

    # Arrancar el bucle del menú interactivo en el hilo principal
    try:
        interactive_menu()
    except KeyboardInterrupt:
        print("\n[!] Emergency shutdown detected. Closing system...")
        sys.exit(0)

if __name__ == "__main__":
    main()