from stx_etx_connection import STXETXConnection
from connection_closed_exception import ConnectionClosedException
from closing_connection_exception import ClosingConnectionException
from engine_data import EngineData

HEALTH_MSG = "req-health-status"
LOCATION_MSG = "req-location"
CENTRAL_FALLEN_MSG = "central-fallen"
CENTRAL_RESTORED_MSG = "central-restored"
PRICE_MSG = "price="

def monitor_handler(monitor_connection: STXETXConnection, data: EngineData):
    try:
        monitor_connection.enq_answer()
        id = monitor_connection.recv_message()
        data.id.set_id(id)
        if data.status.is_stopped():
            data.status.set_active()
    except ConnectionClosedException:
        data.status.set_stopped()
        return
    
    running = True
    while running:
        try:
            petition = monitor_connection.recv_message()
            if petition == HEALTH_MSG:
                monitor_connection.send_message(str(data.status.value))
            elif petition == LOCATION_MSG:
                monitor_connection.send_message(data.location)
            elif petition == CENTRAL_FALLEN_MSG:
                # monitor_connection.send_message("ok")
                data.status.set_stopped()
            elif petition == CENTRAL_RESTORED_MSG:
                # monitor_connection.send_message("ok")
                data.status.set_active()
            elif petition.startswith(PRICE_MSG):
                price = float(petition.removeprefix(PRICE_MSG))
                data.price = price
        except ClosingConnectionException:
            running = False
            monitor_connection.close()
        except ConnectionClosedException:
            data.status.set_stopped()
            return
