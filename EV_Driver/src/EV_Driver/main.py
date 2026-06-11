import sys
import os
import time
import argparse
import signal


from .system.event_bus import EVENT_QUEUE

# 2. Importamos configuración de Kafka y tu clase Driver
from communications.kafka import KafkaBrokerInfo
from .Driver import Driver  


def main():
    # ==========================================
    # CONFIGURACIÓN DE ARGUMENTOS DE CONSOLA
    # ==========================================
    ip = os.getenv("IP")
    broker_ip = os.getenv("BROKER_IP")
    driver_id = os.getenv("ID") 
    cps_file_path = os.getenv("CPS_FILE")
    saved_file_path = os.getenv("SAVED_FILE")
    # 2. Leemos el puerto y lo convertimos a entero de forma segura
    broker_port_str = os.getenv("BROKER_PORT")
    
    # Validación básica: comprobamos que ninguna variable vital esté vacía (None)
    if not all([ip, broker_ip, broker_port_str, driver_id, cps_file_path, saved_file_path]):
        print("ERROR: Missing vital environment variables in the container.")
        sys.exit(1) # Salimos con error para que Docker sepa que el arranque falló

    # Intentamos convertir el puerto a número entero
    try:
        broker_port = int(broker_port_str)
    except ValueError:
        print(f"ERROR: The port provided in BROKER_PORT ({broker_port_str}) is not a valid number.")
        sys.exit(1)
   # ==========================================
    # INICIALIZACIÓN DEL SISTEMA
    # ==========================================
    print(f"[*] Starting system for driver: {driver_id}")
    print(f"[*] Local IP: {ip}")
    print(f"[*] Connecting to Kafka at: {broker_ip}:{broker_port}")
    
    broker_info = KafkaBrokerInfo(broker_ip, broker_port)
    
    
    try:
        # Instanciamos pasando los 4 parámetros correctos
        driver = Driver(broker_info, cps_file_path, saved_file_path, driver_id)
    except Exception as e:
        print(f"[!] Critical error initializing Driver or connecting to Kafka: {e}")
        sys.exit(1)

    # ==========================================
    # EL GRAN BUCLE ORQUESTADOR DE FASES
    # ==========================================
    while True:
        try:
            # FASE 0: COMPROBAR RECUPERACIÓN (CRASH RECOVERY BYPASS)
            if driver.supply_id is not None:
                print(f"RECOVERY ACTIVATED! Bypassing menu. Resuming interrupted supply: {driver.supply_id}")
                print("\n[+] Transitioning directly to TELEMETRY phase...")
                
                # Vamos directos a leer los mensajes que nos perdimos
                driver.supplying_phase()
                
                print("\n[+] Recovered session finished. Returning to main menu...")
                time.sleep(4)
                continue # Volvemos al inicio del while para entrar por la Fase 1 normal

            # FASE 1: Menú interactivo y selección de Punto de Recarga
            driver.start_cp_Listing_phase()
            
            # FASE 2: Motor de conexión con reintentos (Round-Robin)
            conexion_exitosa = False
            
            while driver.cp_list: 
                conexion_exitosa = driver.central_connection_phase(ip)
                
                if conexion_exitosa:
                    break 
                else:
                    time.sleep(0.5) 
                    
            # FASE 3: Transición al Suministro normal
            if conexion_exitosa:
                print("\n[+] Transitioning to TELEMETRY phase (Supply in progress)...")
                
                driver.supplying_phase()
                
                print("\n[+] Charging session finished. Returning to main menu...")
                time.sleep(4)
                
            else:
                print("\n[!] All CPs have been exhausted and none accepted the supply request.")
                print("[*] Returning to main menu to wait for central updates...")
                time.sleep(4)

        except KeyboardInterrupt:
            # Esta señal ahora es interceptada primero por tu clase Driver gracias al 'signal'
            pass

if __name__ == "__main__":
    main()