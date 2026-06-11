import sys
import time
import uuid


from communications.kafka import KafkaBrokerInfo, KafkaFactory
from .system.TerminalHandler import TerminalHandler
from .system.FileHandler import FileHandler
from .kafka.messages import *
from .kafka.kafka_subscribers import *
from .system.event_bus import *

class Driver:
    def __init__(self, broker_info: KafkaBrokerInfo, filename: str, driver_id: str):

        self.driver_id = driver_id
        self.supply_id = None

        self.fileHandler = FileHandler(filename)
        self.cp_list = self.fileHandler.readFileLines()
        self.terminalHandler = TerminalHandler(EVENT_QUEUE)

        self._broker_info = broker_info
        self._kafka_factory = KafkaFactory(broker_info)

        driver_filter_function = lambda msg: self.driver_id == msg.driver_id

#       ---- Consumers que se crean una sola vez ----
        run_id = str(uuid.uuid4())[:8]
        self.cp_listing_consumer = self._kafka_factory.create_consumer("cp.active.listing", f"{self.driver_id}-listing-{run_id}", ActiveCPListingMessage)
        self.supply_error_consumer = self._kafka_factory.create_consumer("supply.errors", f"{self.driver_id}-err-{run_id}", SupplyErrorMessage)
        self.cp_listing_consumer.get_notifier().add_subscriber(cp_listing_handler)
        self.supply_error_consumer.get_notifier().add_subscriber(kafka_error_handler)

#       ---- Consumers de fase supply (se recrean en cada ronda) ----
        self.supply_request_notifications_consumer = None
        self.supply_response_consumer = None
        self.supply_telemetry_consumer = None

#       ---- Producers ----
        self.supply_request_producer = self._kafka_factory.create_producer("supply.request.users")

    def _recreate_supply_consumers(self):
        """Crea instancias frescas de los consumers de supply. Necesario porque
        KafkaConsumer.stop_polling() mata el hilo interno y no puede reutilizarse."""
        driver_filter_function = lambda msg: self.driver_id == msg.driver_id
        run_id = str(uuid.uuid4())[:8]

        self.supply_request_notifications_consumer = self._kafka_factory.create_consumer(
            "supply.request.notifications",
            f"{self.driver_id}-notif-{run_id}",
            SupplyRequestNotificationMessage,
            driver_filter_function
        )
        self.supply_response_consumer = self._kafka_factory.create_consumer(
            "supply.response",
            f"{self.driver_id}-resp-{run_id}",
            SupplyResponseMessage,
            driver_filter_function
        )
        self.supply_telemetry_consumer = self._kafka_factory.create_consumer(
            "supply.telemetry.users",
            f"{self.driver_id}-telem-{run_id}",
            SupplyTelemetryMessage,
            None
        )
        self.supply_request_notifications_consumer.get_notifier().add_subscriber(request_notification_handler)
        self.supply_response_consumer.get_notifier().add_subscriber(response_handler)
        self.supply_telemetry_consumer.get_notifier().add_subscriber(telemetry_info_handler)

    def __next_cp(self):
        self.cp_list.append(self.cp_list.pop(0))

    def start_cp_Listing_phase(self):

# ----- Inicialización
        self.supply_error_consumer.start_polling()
        self.cp_listing_consumer.start_polling()
        self.terminalHandler.start_listening()

        while True:
            TerminalHandler.printCP(self.cp_list)
    # ----- Esperamos los eventos que tengan la intención KEYBOARD_INPUT, UPDATE_CPS o KAFKA_ERROR
            event = wait_for_events(Intention.KAFKA_ERROR, Intention.UPDATE_CPS, Intention.KEYBOARD_INPUT)
            match event.intention:
                case Intention.KEYBOARD_INPUT:
                    command = str(event.data).strip().lower()
                    if command == 'q':
                        sys.exit(0)

                    if not self.cp_list:
                        continue

                    elif command.isdigit():
                        index = int(command)
                        
                        # Comprobamos que el número esté dentro del rango válido
                        if 1 <= index <= len(self.cp_list):
                            # Mapeamos el índice visual (1) al índice real de Python (0)
                            objective_id = self.cp_list[index - 1]
                            
                            # Rotamos la lista hasta ponerlo el primero
                            while self.cp_list[0] != objective_id:
                                self.__next_cp()
                            
                            break # ¡Rompemos el bucle para ir a suministrar!
                        else:
                            print(f"\n[!] El número {index} no está en la lista. Conectando en automático...")
                            break
                            
                    # 3. SI HA ESCRITO EL ID LITERAL (Por si acaso)
                    elif command in [cp.lower() for cp in self.cp_list]:
                        # Rotamos la lista usando el nombre literal
                        while self.cp_list[0].lower() != command:
                            self.__next_cp()
                        
                        break # ¡Rompemos el bucle para ir a suministrar!
                        
                    # 4. SI HA DADO AL ENTER SIN MÁS (Automático)
                    else:
                        print(f"\n[!] Input ignorado. Conectando al siguiente CP en automático...")
                        break
                                            
                    
                case Intention.UPDATE_CPS:
                    print("Actualizando los puntos de recarga...")
                    self.cp_list = event.data
                    self.fileHandler.writeList(self.cp_list)
                    continue
                    
                case Intention.KAFKA_ERROR:
                    print(f"\n[!] System Error: {event.data}")
                    print("The menu will be displayed...")
                    time.sleep(3)
                    continue
        
# ----- Finalize
        self.terminalHandler.stop_listening()
        self.cp_listing_consumer.stop_polling()


    def central_connection_phase(self, driver_ip: str):

        method_result = False

# ----- Recrear consumers frescos para esta ronda
        self._recreate_supply_consumers()

# ----- Iniciar loops de consumers
        self.supply_response_consumer.start_polling()
        self.supply_request_notifications_consumer.start_polling()
        self.supply_telemetry_consumer.start_polling()

        # Dale tiempo a Kafka para negociar la unión al grupo y fijar el offset
        print("Wait a moment to sync connections...")
        time.sleep(2)

# ----- Producer del mensaje supply request
        if not self.cp_list:
            print("No CPs Available")
            print("Restarting, sorry for the inconvenience")
            return False
        
        print(f"Trying connection with the cp \"{self.cp_list[0]}\" ")

        self.supply_request_producer.send_message(SupplyRequestMessage(self.driver_id, self.cp_list[0], driver_ip))
        print("Message sent, wait a few seconds...")

        while True:
            event = wait_for_events(Intention.KAFKA_ERROR, Intention.ACCEPTED_RESPONSE, Intention.DENIED_RESPONSE, Intention.NOTIFICATIONS)
            match event.intention:
                case Intention.KAFKA_ERROR:
                    print(f"\n[!] System Error: {event.data}")
                    print("The menu will be displayed...")
                    time.sleep(3)
                    continue
                
                case Intention.ACCEPTED_RESPONSE:
                    print(f"Driver successfully connected (supply Id = {event.data})")
                    self.supply_id = event.data
                    method_result = True
                    break

                case Intention.DENIED_RESPONSE:
                    print(f"REFUSED CONNECTION: {event.data}")
                    self.cp_list.pop(0)
                    break

                case Intention.NOTIFICATIONS:
                    print(f"Central - {event.data}")
                    continue
        
# ----- Finalize
        self.supply_response_consumer.stop_polling()
        self.supply_request_notifications_consumer.stop_polling()
        if not method_result:
            # Solo paramos telemetría aquí si fue denegado (si fue aceptado, la para supplying_phase)
            self.supply_telemetry_consumer.stop_polling()
        return method_result
                
        
    def supplying_phase(self):
        print("\n[+] Transitioning to TELEMETRY phase (Supply in progress)...")

        while True:
            event = wait_for_events(Intention.KAFKA_ERROR, Intention.TELEMETRY_INFO, Intention.TELEMETRY_TICKET)
            match event.intention:
                case Intention.KAFKA_ERROR:
                    print(f"\n[!] System Error: {event.data}")
                    print("The menu will be displayed...")
                    time.sleep(3)
                    continue
                
                case Intention.TELEMETRY_INFO:
                    if event.data.supply_id == self.supply_id:
                        TerminalHandler.printSupplyingInfo(event.data.price, event.data.consumption)
                    continue

                case Intention.TELEMETRY_TICKET:
                    if event.data.supply_id == self.supply_id:
                        TerminalHandler.printSupplyingTicket(event.data.price, event.data.consumption)
                        self.supply_id = None
                        break
                    continue
        
# ----- Finalize
        self.supply_telemetry_consumer.stop_polling()
