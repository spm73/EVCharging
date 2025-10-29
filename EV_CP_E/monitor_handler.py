from stx_etx_connection import STXETXConnection
from connection_closed_exception import ConnectionClosedException
from closing_connection_exception import ClosingConnectionException
from engine_data import EngineData
import threading

HEALTH_MSG = "req-health-status"
LOCATION_MSG = "req-location"
CENTRAL_FALLEN_MSG = "central-fallen"
CENTRAL_RESTORED_MSG = "central-restored"
PRICE_MSG = "price="

def monitor_handler(monitor_connection: STXETXConnection, data: EngineData, lock: threading.Lock):
    """
    Handler para las peticiones del monitor.
    Ahora recibe un lock para sincronización thread-safe con el resto del engine.
    """
    try:
        monitor_connection.enq_answer()
        id = monitor_connection.recv_message()
        
        # Cambio thread-safe del ID
        with lock:
            data.id.set_id(id)
            if data.status.is_stopped():
                data.status.set_active()
                
    except ConnectionClosedException:
        with lock:
            data.status.set_stopped()
        return
    
    running = True
    while running:
        try:
            petition = monitor_connection.recv_message()
            
            if petition == HEALTH_MSG:
                with lock:
                    monitor_connection.send_message(str(data.status.value))
                
            elif petition == LOCATION_MSG:
                monitor_connection.send_message(data.location)
                
            elif petition == CENTRAL_FALLEN_MSG:
                with lock:
                    print("\n[MONITOR] Central has fallen - CP going to STOPPED state")
                    data.status.set_stopped()
                
            elif petition == CENTRAL_RESTORED_MSG:
                with lock:
                    print("\n[MONITOR] Central has been restored - CP going to ACTIVE state")
                    data.status.set_active()
                
            elif petition.startswith(PRICE_MSG):
                price = float(petition.removeprefix(PRICE_MSG))
                with lock:
                    data.price = price
                    print(f"\n[MONITOR] Price updated to {price}€/kWh")
                    
        except ClosingConnectionException:
            running = False
            monitor_connection.close()
            print("\n[MONITOR] Connection closed gracefully")
            
        except ConnectionClosedException:
            with lock:
                data.status.set_stopped()
            print("\n[MONITOR] Connection lost - CP set to STOPPED")
            return