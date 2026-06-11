import os
import signal
import sys
import threading
import uvicorn
from fastapi import FastAPI

from EV_Central.models.Base import Base
from EV_Central.state.Database import Database

from EV_Central.api.cps import router as cp_router
from EV_Central.api.events import router as event_router
from EV_Central.api.drivers import router as driver_router
from EV_Central.api.transactions import router as transaction_router

from EV_Central.state.KafkaManager import KafkaManager
from communications.kafka import KafkaBrokerInfo
from EV_Central.kafka.kafka_subscribers import driver_request_handler, cp_request_handler, resend_telemetry
from EV_Central.kafka.kafka_encripted_subscribers import cp_encrypted_request_handler, resend_encrypted_telemetry
from EV_Central.kafka.messages import SupplyRequestMessage, SupplyTelemetryMessage, EncryptedMessage

from communications.sockets import SocketServer
from EV_Central.sockets.handle_monitor import handle_monitor

app = FastAPI()
app.include_router(cp_router)
app.include_router(event_router)
app.include_router(driver_router)
app.include_router(transaction_router)

# Event to block the main thread until a shutdown signal is received
shutdown_event = threading.Event()

def start_api() -> None:
    api_port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run(app, host="0.0.0.0", port=api_port)
    
def main():
    print("=========================================")
    print(" Starting EV_Central")
    print("=========================================\n")

    print("[Main] Initializing database tables...")
    try:
        Base.metadata.create_all(bind=Database().get_engine())
    except Exception as e:
        print(f"[Error] Failed to create tables: {e}")

    # 1. Kafka Manager and Consumers Configuration
    kafka_host = os.getenv("KAFKA_BROKER_HOST", "127.0.0.1")
    kafka_port = int(os.getenv("KAFKA_BROKER_PORT", "9092"))
    
    broker_info = KafkaBrokerInfo(kafka_host, kafka_port)
    kafka_manager = KafkaManager(broker_info)
    factory = kafka_manager.get_factory()
    
    group_id = "central_group"
    consumers = []
    
    try:
        consumers.append(factory.create_consumer("supply.request.users", f"{group_id}_users", SupplyRequestMessage, None))
        consumers[-1].get_notifier().add_subscriber(driver_request_handler)
        
        consumers.append(factory.create_consumer("supply.request.cps", f"{group_id}_cps", EncryptedMessage, None))
        consumers[-1].get_notifier().add_subscriber(cp_encrypted_request_handler)
        
        consumers.append(factory.create_consumer("supply.telemetry.cp", f"{group_id}_telemetry", EncryptedMessage, None))
        consumers[-1].get_notifier().add_subscriber(resend_encrypted_telemetry)

        print("[Main] Starting Kafka Consumers...")
        for c in consumers:
            c.start_polling()
            
    except Exception as e:
        print(f"[Error] Failed to start Kafka consumers: {e}")

    # 2. Socket Server Configuration and Startup
    listen_ip = os.getenv("LISTENING_IP", "0.0.0.0")
    listen_port = int(os.getenv("LISTENING_PORT", "7000"))
    
    print(f"[Main] Starting Socket Server on {listen_ip}:{listen_port}...")
    socket_server = SocketServer(
        ip=listen_ip,
        port=listen_port,
        handler=handle_monitor
    )
    socket_server.start()
    
    # 3. API Startup (in background thread)
    print(f"[Main] Starting FastAPI...")
    api_thread = threading.Thread(target=start_api, daemon=True)
    api_thread.start()

    # 4. Graceful Shutdown Configuration
    def signal_handler(sig, frame):
        print("\n[Main] Termination signal received. Shutting down EV_Central...")
        shutdown_event.set()

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Block main thread until signal is received
    shutdown_event.wait()

    # Clean shutdown process
    print("[Main] Stopping Socket Server...")
    socket_server.stop()
    
    print("[Main] Stopping Kafka Consumers...")
    for c in consumers:
        c.stop_polling()
        
    print("[Main] Shutdown completed.")
    sys.exit(0)

if __name__ == "__main__":
    main()
