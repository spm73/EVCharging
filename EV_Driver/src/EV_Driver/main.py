import sys
import os
import time
import argparse


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
    file_path = os.getenv("FILE")
    
    # 2. Leemos el puerto y lo convertimos a entero de forma segura
    broker_port_str = os.getenv("BROKER_PORT")
    
    # Validación básica: comprobamos que ninguna variable vital esté vacía (None)
    if not all([ip, broker_ip, broker_port_str, driver_id, file_path]):
        print("ERROR: Missing vital environment variables in the container.")
        sys.exit(1) # Salimos con error para que Docker sepa que el arranque falló

    # Intentamos convertir el puerto a número entero
    try:
        broker_port = int(broker_port_str)
    except ValueError:
        print(f"❌ ERROR: The port provided in BROKER_PORT ({broker_port_str}) is not a valid number.")
        sys.exit(1)
    # ==========================================
    # INICIALIZACIÓN DEL SISTEMA
    # ==========================================
    print(f"[*] Starting system for driver: {driver_id}")
    print(f"[*] Local IP: {ip}")
    print(f"[*] Connecting to Kafka at: {broker_ip}:{broker_port}")
    
    # Creamos el objeto de información del Broker
    # (Asumiendo que el constructor recibe IP y Puerto)
    broker_info = KafkaBrokerInfo(broker_ip, broker_port)
    
    try:
        # Instanciamos tu super-clase Driver
        driver = Driver(broker_info, file_path, driver_id)
    except Exception as e:
        print(f"[!] Critical error initializing Driver or connecting to Kafka: {e}")
        sys.exit(1)

    # ==========================================
    # EL GRAN BUCLE ORQUESTADOR DE FASES
    # ==========================================
    while True:
        try:
            # FASE 1: Menú interactivo y selección de Punto de Recarga
            # (El programa se bloquea aquí hasta que el usuario decida o haya un evento automático)
            driver.start_cp_Listing_phase()
            
            # FASE 2: Motor de conexión con reintentos (Round-Robin)
            conexion_exitosa = False
            
            # Mientras la lista del driver tenga CPs, intentamos conectar
            while driver.cp_list: 
                conexion_exitosa = driver.central_connection_phase(ip)
                
                if conexion_exitosa:
                    # Si devuelve True, el suministro fue aceptado. Rompemos el bucle de reintentos.
                    break 
                else:
                    # Si devuelve False, fue denegado. Damos un respiro antes de atacar al siguiente CP.
                    time.sleep(0.5) 
                    
            # FASE 3: Transición al Suministro (Telemetría)
            if conexion_exitosa:
                print("\n[+] Transitioning to TELEMETRY phase (Supply in progress)...")
                
                # Lanzamos tu último método. Se quedará aquí hasta que llegue el TELEMETRY_TICKET
                driver.supplying_phase()
                
                # Cuando supplying_phase termina, el coche se ha desconectado.
                # El bucle while True dará la vuelta y volveremos al menú de CPs.
                print("\n[+] Charging session finished. Returning to main menu...")
                time.sleep(2)
                
            else:
                # Si llegamos aquí, es que agotamos toda la lista de CPs en la Fase 2 y ninguno funcionó
                print("\n[!] All CPs have been exhausted and none accepted the supply request.")
                print("[*] Returning to main menu to wait for central updates...")
                time.sleep(2)

        except KeyboardInterrupt:
            # Si el usuario pulsa Ctrl+C en cualquier momento para abortar bruscamente
            print("\n[!] Emergency shutdown detected (Ctrl+C). Closing system...")
            sys.exit(0)

if __name__ == "__main__":
    main()