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
                
                # --- NUEVO: Iniciar consumers para el modo recuperación ---
                # 1. Iniciamos el de errores (que normalmente se inicia en Fase 1)
                driver.supply_error_consumer.start_polling()
                
                # 2. Recreamos los de supply y arrancamos el de telemetría (Fase 2)
                driver._recreate_supply_consumers()
                driver.supply_telemetry_consumer.start_polling()
                # -----------------------------------------------------------
                
                # Vamos directos a leer los mensajes que nos perdimos
                driver.supplying_phase()
                
                print("\n[+] Recovered session finished. Returning to main menu...")
                time.sleep(4)
                continue # Volvemos al inicio del while para entrar por la Fase 1 normal# Volvemos al inicio del while para entrar por la Fase 1 normal

            # FASE 1: Menú interactivo y selección de Punto de Recarga
            driver.start_cp_Listing_phase()
            
            # FASE 2: Intento ÚNICO de conexión 
            conexion_exitosa = driver.central_connection_phase(ip)
                    
            # FASE 3: Transición o Retorno
            if conexion_exitosa:
                driver.supplying_phase()
                
                print("\n[+] Charging session finished. Returning to main menu...")
                time.sleep(4)
                
            else:
                print("\n[!] CP denied the connection. Returning to menu to pick another...")
                time.sleep(1.5)
                # Recargamos la lista completa desde el fichero para que el menú vuelva a mostrarlos todos en el orden original
                driver.cp_list = driver.cps_fileHandler.readFileLines()
                
                # Al terminar aquí, el 'while True' principal volverá a arrancar la Fase 1 automáticamente

        except KeyboardInterrupt:
            # Capturamos el Ctrl+C para hacer una salida limpia sin ensuciar la terminal
            print("\n[!] Program interrupted by user. Exiting cleanly...")
            sys.exit(0)

if __name__ == "__main__":
    main()