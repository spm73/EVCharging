import os
import threading
import time
from communications.kafka import KafkaBrokerInfo, SimpleKafkaFactory, KafkaProducer


class Driver:
    def __init__(self, file_path: str, broker_info: KafkaBrokerInfo):
        self.file_path = file_path
        # Usamos la factory para crear todo lo relacionado con Kafka
        self.factory = SimpleKafkaFactory(broker_info)
        
        self.available_cps: list[str] = []
        self.list_lock = threading.Lock()
        self.response_received_event = threading.Event()
        self.current_response = None
        
        # 1. Cargar datos previos
        self._load_cps_from_file()
        
        # 2. Iniciar el hilo permanente de escucha de CPs
        self._start_cp_listing_listener()

def _load_cps_from_file(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                cps = [line.strip() for line in f.readlines() if line.strip()]
                with self.list_lock:
                    self.available_cps.extend(cps)
            print(f"[*] CPs cargados del archivo: {len(self.available_cps)}")

def _start_cp_listing_listener(self):
        # Creamos el consumidor usando la factory de tu amigo
        self.cp_listener = self.factory.create_consumer(
            topic="",
            group_id="",
            message_class=ActiveCPListingMessage
        )
        
        # Usamos el notifier y add_subscriber como indica su archivo KafkaNotifier.py
        self.cp_listener.get_notifier().add_subscriber(self._handle_new_cps)
        self.cp_listener.start_polling()

def _handle_new_cps(self, message: ActiveCPListingMessage):
        with self.list_lock:
            for cp in message.active_cps:
                if cp not in self.available_cps:
                    self.available_cps.append(cp)
                    # Aquí podrías añadir la lógica para escribir en el archivo
        print(f"\n[+] Lista actualizada. Total CPs: {len(self.available_cps)}")


def iniciar_proceso_supply(self, start_index: int):
        current_index = start_index
        
        # Creamos un productor para enviar la petición
        producer = self.factory.create_producer(topic="supply-request-topic")

        while True:
            with self.list_lock:
                if current_index >= len(self.available_cps):
                    print("[-] No hay más CPs disponibles en la lista.")
                    break
                cp_actual = self.available_cps[current_index]

            print(f"\n>>> Solicitando Supply al CP: {cp_actual}")
            
            # Enviamos el mensaje usando el productor
            msg_request = SupplyRequestMessage(cp_id=cp_actual)
            producer.send_message(msg_request)

            # Configuramos la espera de respuesta
            self.response_received_event.clear()
            
            # Consumidores temporales para este intento
            res_cons = self.factory.create_consumer("supply-response", f"res-{cp_actual}", SupplyResponseMessage)
            not_cons = self.factory.create_consumer("supply-notif", f"not-{cp_actual}", SupplyRequestNotificationMessage)

            res_cons.get_notifier().add_subscriber(self._on_response)
            not_cons.get_notifier().add_subscriber(lambda m: print(f"    [Estado]: {m.status}"))

            res_cons.start_polling()
            not_cons.start_polling()

            # Bloqueamos hasta que llegue el mensaje de confirmación/denegación
            self.response_received_event.wait()

            # Limpieza de hilos temporales
            res_cons.stop_polling()
            not_cons.stop_polling()

            if self.current_response.is_positive:
                print(f"[OK] Conectado con éxito a {cp_actual}")
                # Aquí llamarías a los siguientes pasos que mencionaste
                break 
            else:
                print(f"[!] {cp_actual} rechazó la conexión. Reintentando con el siguiente...")
                current_index += 1

    def _on_response(self, message: SupplyResponseMessage):
        pass