import os
import signal
import sys
import threading

from EV_CP_E.CPEngine import CPEngine
from EV_CP_E.Event import Event
from EV_CP_E.EventType import EventType
from EV_CP_E.monitor_handler import socket_handler

from communications.kafka.KafkaBrokerInfo import KafkaBrokerInfo
from communications.kafka.KafkaFactory import KafkaFactory
from EV_CP_E.kafka.messages.EncryptedMessage import EncryptedMessage
from communications.sockets.SocketServer import SocketServer
from EV_CP_E.CheckpointManager import CheckpointManager
from EV_CP_E.ui import EngineApp


def main():
    # Configuración de entorno (Docker Compose pasará estas variables)
    engine_ip = os.getenv("ENGINE_HOST", "0.0.0.0")
    engine_port = int(os.getenv("ENGINE_PORT", "9000"))
    kafka_ip = os.getenv("KAFKA_BROKER_HOST", "127.0.0.1")
    kafka_port = int(os.getenv("KAFKA_BROKER_PORT", "9092"))
    
    print("=========================================")
    print(f" Starting EV_CP_E (Engine)")
    print(f" Socket Port : {engine_port}")
    print(f" Kafka Broker: {kafka_ip}:{kafka_port}")
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
    print(f"[Main] SocketServer listening on {engine_ip}:{engine_port}")

    # (Los consumidores de Kafka se inician dinámicamente cuando el Engine 
    # recibe el CONFIG con el cp_id desde el monitor).

    # 4. Manejo de señales para apagado controlado
    def signal_handler(sig, frame):
        print("\n[Main] Received termination signal (SIGINT/SIGTERM). Initiating shutdown...")
        engine.put_event(Event(EventType.SHUTDOWN))

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # 5. Bucle de eventos principal (en un hilo)
    def run_engine_loop():
        print("[Main] Entering main event loop...")
        while engine.handle_next_event():
            pass

        # --- FASE DE APAGADO (Graceful Shutdown) ---
        print("[Main] Closing SocketServer...")
        server.stop()

        print("[Main] Closing Kafka consumers...")
        engine.stop_kafka_consumers()

        print("[Main] Saving state (Checkpoint)...")
        CheckpointManager().save(engine.get_checkpoint_data())
        
        print("[Main] Shutdown completed.")

    engine_thread = threading.Thread(target=run_engine_loop)
    engine_thread.start()

    # 6. Interfaz UI (Textual) bloqueante en el hilo principal
    try:
        EngineApp().run()
    except Exception as e:
        print(f"[Main] UI error: {e}")

    # Cuando la UI termina (por la tecla 'q' o Ctrl+C)
    print("\n[Main] UI closed. Initiating shutdown...")
    engine.put_event(Event(EventType.SHUTDOWN))
    engine_thread.join()
    sys.exit(0)


if __name__ == "__main__":
    main()
