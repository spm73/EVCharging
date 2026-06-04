import os
import signal
import sys
import threading

from .CPEngine import CPEngine
from .Event import Event
from .EventType import EventType
from .monitor_handler import socket_handler

from communications.kafka.KafkaBrokerInfo import KafkaBrokerInfo
from communications.kafka.KafkaFactory import KafkaFactory
from .kafka.messages.EncryptedMessage import EncryptedMessage
from communications.sockets.SocketServer import SocketServer
from .CheckpointManager import CheckpointManager
from .ui import EngineApp


def main():
    # Configuración de entorno (Docker Compose pasará estas variables)
    engine_ip = os.getenv("ENGINE_IP", "0.0.0.0")
    engine_port = int(os.getenv("ENGINE_PORT", "9000"))
    kafka_ip = os.getenv("KAFKA_BROKER_IP", "127.0.0.1")
    kafka_port = int(os.getenv("KAFKA_BROKER_PORT", "9092"))
    
    print("=========================================")
    print(f" Iniciando EV_CP_E (Engine)")
    print(f" Puerto Socket : {engine_port}")
    print(f" Kafka Broker  : {kafka_ip}:{kafka_port}")
    print("=========================================\n")

    # 1. Instanciar el Singleton del Engine
    engine = CPEngine()

    # 2. Configurar Kafka
    broker_info = KafkaBrokerInfo(kafka_ip, kafka_port)
    kafka_factory = KafkaFactory(broker_info)
    engine.set_kafka_factory(kafka_factory)

    # 3. Iniciar el SocketServer (comunicación con EV_CP_M)
    server = SocketServer(
        ip=engine_ip,
        port=engine_port,
        handler=socket_handler
    )
    server.start()
    print(f"[Main] SocketServer escuchando en {engine_ip}:{engine_port}")

    # (Los consumidores de Kafka se inician dinámicamente cuando el Engine 
    # recibe el CONFIG con el cp_id desde el monitor).

    # 4. Manejo de señales para apagado controlado
    def signal_handler(sig, frame):
        print("\n[Main] Recibida señal de terminación (SIGINT/SIGTERM). Iniciando apagado...")
        engine.put_event(Event(EventType.SHUTDOWN))

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 5. Bucle de eventos principal (en un hilo)
    def run_engine_loop():
        print("[Main] Entrando en el bucle de eventos principal...")
        while engine.handle_next_event():
            pass

        # --- FASE DE APAGADO (Graceful Shutdown) ---
        print("[Main] Cerrando SocketServer...")
        server.stop()

        print("[Main] Cerrando consumidores de Kafka...")
        engine.stop_kafka_consumers()

        print("[Main] Guardando estado (Checkpoint)...")
        CheckpointManager().save(engine.get_checkpoint_data())
        
        print("[Main] Apagado completado.")

    engine_thread = threading.Thread(target=run_engine_loop)
    engine_thread.start()

    # 6. Interfaz UI (Textual) bloqueante en el hilo principal
    try:
        EngineApp().run()
    except Exception as e:
        print(f"[Main] Error en UI: {e}")

    # Cuando la UI termina (por la tecla 'q' o Ctrl+C)
    print("\n[Main] UI cerrada. Iniciando apagado...")
    engine.put_event(Event(EventType.SHUTDOWN))
    engine_thread.join()
    sys.exit(0)


if __name__ == "__main__":
    main()
