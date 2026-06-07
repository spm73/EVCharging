import sys
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
    parser = argparse.ArgumentParser(description="Smart Charging - Driver Client Application")
    
    # Argumentos de Red Local
    parser.add_argument('--ip', type=str, required=True, help="IP de la máquina local (Conductor)")
    
    # Argumentos del Servidor Kafka
    parser.add_argument('--broker-ip', type=str, required=True, help="IP del servidor central Kafka")
    parser.add_argument('--broker-port', type=int, required=True, help="Puerto del servidor Kafka (ej. 9092)")
    
    # Argumentos de Lógica de Negocio
    parser.add_argument('--id', type=str, required=True, help="ID único de este conductor (ej. DRV-01)")
    parser.add_argument('--file', type=str, required=True, help="Nombre del archivo .txt inicial de CPs")

    # Parseamos lo que el usuario haya escrito en la terminal
    args = parser.parse_args()

    # ==========================================
    # INICIALIZACIÓN DEL SISTEMA
    # ==========================================
    print(f"[*] Starting system for driver: {args.id}")
    print(f"[*] Local IP: {args.ip}")
    print(f"[*] Connecting to Kafka at: {args.broker_ip}:{args.broker_port}")
    
    # Creamos el objeto de información del Broker
    # (Asumiendo que el constructor recibe IP y Puerto)
    broker_info = KafkaBrokerInfo(args.broker_ip, args.broker_port)
    
    try:
        # Instanciamos tu super-clase Driver
        driver = Driver(broker_info, args.file, args.id)
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
                conexion_exitosa = driver.central_connection_phase(args.ip)
                
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