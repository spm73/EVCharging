import sys
import select
import threading
import time
from confluent_kafka import KafkaException

from engine_config import EngineConfig
from directives_consumer import DirectivesConsumer
from supply_req_producer import SupplyReqProducer
from supply_res_consumer import SupplyResConsumer
from supply_info import SupplyInfo
from monitor_handler import monitor_handler
from monitor_server import MonitorServer
from engine_data import EngineData

class EngineApp:
    def __init__(self):
        self.config = EngineConfig()
        self.cp_data = EngineData(self.config.location)
        self.monitor_server = MonitorServer(self.config.server_ip, self.config.server_port)
        self.directives_consumer = None
        self.supply_info = None
        self.supply_id = None
        self.running = True
        self.monitor_connected = False
        self.directive_thread = None
        self.pending_supply_start = False
        self.lock = threading.Lock()
        self.id_received = threading.Event()
        self.supply_directive_event = threading.Event()

    def wait_for_monitor(self):
        """Espera a que el monitor se conecte antes de continuar"""
        print("=" * 60)
        print("EV_CP_E - Charging Point Engine")
        print("=" * 60)
        print(f"CP ID: {self.cp_data.id.get_id()}")
        print(f"Location: {self.cp_data.location}")
        print(f"Listening on {self.config.server_ip}:{self.config.server_port}")
        print("\nWaiting for Monitor to connect...")
        print("=" * 60)
        
        self.monitor_server.listen()
        self.monitor_server.accept(monitor_handler, self.cp_data, self.lock, self.id_received)
        
        self.id_received.wait(timeout=30)
        if not self.cp_data.id.get_id():
            raise Exception("Failed to receive CP ID from Monitor")
        
        self.monitor_connected = True
        print("\n✓ Monitor connected successfully!")
        print("=" * 60)
        #time.sleep(1)

    def handle_directives_thread(self):
        """Hilo que constantemente escucha directivas de la central"""
        while self.running:
            try:
                directive = self.directives_consumer.get_directive()
                
                if not directive:
                    #time.sleep(0.1)
                    continue
                
                with self.lock:
                    self._process_directive(directive)
                    
            except KafkaException as e:
                error = str(e.args[0])
                print(f"\n[ERROR] Kafka error in directives: {error}")
                #time.sleep(1)
            except Exception as e:
                print(f"\n[ERROR] Unexpected error in directives thread: {e}")
                #time.sleep(1)

    def _process_directive(self, directive):
        """Procesa una directiva recibida de la central"""
        action = directive.get('action')
        
        if action == 'start-supply' and self.cp_data.status.is_active():
            self.supply_id = directive.get('supply_id')
            self.pending_supply_start = True
            print(f"\n\n[CENTRAL] Supply request received (ID: {self.supply_id})")
            print("[INFO] Waiting for driver to plug the vehicle...")
            self.supply_directive_event.set()
                
        elif action == 'stop' and self.cp_data.status.is_active() or self.cp_data.status.is_waiting_for_supply():
            self.cp_data.status.set_stopped()
            print("\n\n[CENTRAL] CP has been STOPPED by Central")
            print("[INFO] CP is now OUT OF SERVICE")
            self.show_initial_menu()
                
        elif action == 'stop' and self.cp_data.status.is_supplying() and self.supply_info:
            print("\n\n[CENTRAL] EMERGENCY STOP during supply!")
            self.cp_data.status.set_active()
            self.supply_info.send_ticket()
            print("[INFO] Supply terminated. Ticket sent.")
            self.supply_info = None
            self.show_initial_menu()
                
        elif action == 'resume' and self.cp_data.status.is_stopped():
            self.cp_data.status.set_active()
            print("\n\n[CENTRAL] CP has been RESUMED by Central")
            print("[INFO] CP is now ACTIVE and available")
            self.show_initial_menu()

    def show_initial_menu(self):
        """Muestra el menú inicial del CP"""
        print("\n" + "=" * 60)
        # print(f"CP Status: {self.cp_data.status.get_status_name()}")
        print("=" * 60)
        print("OPTIONS:")
        print("  [ENTER] - Start manual supply (without driver app)")
        print("  [q]     - Shutdown engine")
        print("=" * 60)
        print("Waiting for input or driver connection via Central...")

    def request_manual_supply(self):
        """Solicita un suministro manual (sin app del conductor)"""
        print("\n[MANUAL SUPPLY] Requesting authorization from Central...")
        
        supply_request = SupplyReqProducer(self.config.kafka_ip, self.config.kafka_port)
        supply_response = SupplyResConsumer(self.config.kafka_ip, self.config.kafka_port, self.cp_data.id.get_id())
        
        supply_request.send_request(self.cp_data.id.get_id())
        print("[CENTRAL] Checking if CP is available for supply...")
        
        response = None
        
        while not response:
            try:
                response = supply_response.get_response()
            except KafkaException as e:
                error = str(e.args[0])
                print(f"[ERROR] {error}")
                #time.sleep(0.5)
                continue
        
        supply_response.close()
        
        if response['status'] == 'denied':
            print(f"[CENTRAL] Supply DENIED")
            print(f"[REASON] {response['reason']}")
            return False
        
        print("[CENTRAL] Supply AUTHORIZED")
        return True

    def wait_for_supply_directive(self, timeout=180):
        print("[INFO] Waiting for supply directive from Central...")
        
        # Bloqueo eficiente: el thread se duerme hasta que se señalice el evento
        if self.supply_directive_event.wait(timeout=timeout):
            self.supply_directive_event.clear()  # Resetear para próximo uso
            
            with self.lock:
                if self.pending_supply_start:
                    self.pending_supply_start = False
                    return self.supply_id
            
            return None
        else:
            # Timeout
            print(f"[ERROR] Timeout ({timeout}s) waiting for supply directive")
            return None

    def execute_supply(self, supply_id):
        """Ejecuta el suministro de energía"""
        print("\n" + "=" * 60)
        print(f"SUPPLY ID: {supply_id}")
        print("=" * 60)
        print("Do you want to plug the car? (y/n) [default: y]")
        
        ready, _, _ = select.select([sys.stdin], [], [], 0)
        
        if ready:
            response = sys.stdin.readline().strip().lower()
            if response == 'n':
                print("\n[INFO] Supply cancelled by operator")
                return
        else:
            # Si no hay respuesta inmediata, asumir 'y'
            pass
        
        # Iniciar suministro
        self.cp_data.status.set_supplying()
        self.supply_info = SupplyInfo(self.config.kafka_ip, self.config.kafka_port, supply_id, self.cp_data.price)
        
        print("\n" + "=" * 60)
        print("SUPPLYING ENERGY")
        print("=" * 60)
        print("Press [ENTER] to unplug and finish supply")
        print("-" * 60)
        
        time_ini = time.time()
        
        while self.cp_data.status.is_supplying():
            time_elapsed = time.time() - time_ini
            
            with self.lock:
                if not self.cp_data.status.is_supplying():
                    break
                    
                self.supply_info.send_info()
                amount = self.supply_info.get_consumption()
                cost = self.supply_info.get_cost()
            
            print(f"\rTime: {time_elapsed:.2f}s | Energy: {amount:.4f} kWh | Cost: {cost:.4f} €", 
                  end="", flush=True)
            
            # Comprobar si se pulsa ENTER para desenchufar
            if select.select([sys.stdin], [], [], 0.1)[0]:
                sys.stdin.readline()  # Limpiar buffer
                print("\n\n[INFO] Vehicle unplugged by operator")
                self.cp_data.status.set_active()
                break
        
        # Enviar ticket final
        if self.supply_info:
            self.supply_info.send_ticket()
            print("\n" + "=" * 60)
            print("SUPPLY COMPLETED - Thank you for using our service! :)")
            print("=" * 60)
            self.supply_info = None

    def run(self):
        """Función principal de ejecución"""
        # 1. Esperar al monitor
        self.wait_for_monitor()
        
        # 2. Iniciar consumer de directivas
        print(f"CP_ID: {self.cp_data.id.get_id()}")
        self.directives_consumer = DirectivesConsumer(
            self.config.kafka_ip, 
            self.config.kafka_port, 
            self.cp_data.id.get_id()
        )
        
        # 3. Iniciar hilo para escuchar directivas
        self.directive_thread = threading.Thread(target=self.handle_directives_thread, daemon=True)
        self.directive_thread.start()
        
        # 4. Mostrar menú inicial
        self.show_initial_menu()
        
        # 5. Bucle principal
        while self.running:
            # Comprobar si hay directiva pendiente de supply
            with self.lock:
                if self.pending_supply_start:
                    supply_id = self.supply_id
                    self.pending_supply_start = False
                    self.supply_directive_event.clear()
                    self.execute_supply(supply_id)
                    self.show_initial_menu()
                    continue
            
            # Esperar input del usuario
            if select.select([sys.stdin], [], [], 0.5)[0]:
                key = sys.stdin.read(1)
                
                if key == '\n':  # ENTER - suministro manual
                    if not self.cp_data.status.is_active():
                        print("\n[ERROR] CP is not active. Cannot start supply.")
                        print(f"Current status: {self.cp_data.status.get_status_name()}")
                        continue
                    
                    # Solicitar autorización manual
                    if self.request_manual_supply():
                        # Esperar directiva de la central
                        self.supply_directive_event.clear()
                        supply_id = self.wait_for_supply_directive()
                        #supply_id = self.supply_id
                        if supply_id:
                            self.execute_supply(supply_id)
                        else:
                            print("[ERROR] Failed to receive supply directive")
                    
                    self.show_initial_menu()
                    
                elif key.lower() == 'q':  # Apagar
                    print("\n[INFO] Shutting down engine...")
                    self.running = False
                    break
        
        # Cleanup
        print("\n[INFO] Engine stopped")
        if self.directives_consumer:
            self.directives_consumer.close()


def main():
    app = EngineApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n\n[INFO] Engine interrupted by user")
    except Exception as e:
        print(f"\n[ERROR] Fatal error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("[INFO] Cleanup completed")


if __name__ == '__main__':
    main()