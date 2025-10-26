from stx_etx_connection import STXETXConnection
from connection_closed_exception import ConnectionClosedException
from closing_connection_exception import ClosingConnectionException
from cp_status import CPStatus
from cp_id import CPId

HEALTH_MSG = "req-health-status"
LOCATION_MSG = "req-location"
CENTRAL_FALLEN_MSG = "central-fallen"
CENTRAL_RESTORED_MSG = "central-restored"
PRICE_MSG = "price="

def monitor_handler(monitor_connection: STXETXConnection, status: CPStatus, cp_id: CPId, location: str):
    try:
        monitor_connection.enq_answer()
        id = monitor_connection.recv_message()
        cp_id.set_id(id)
        if status.is_stopped():
            status.set_active()
    except ConnectionClosedException:
        status.set_stopped()
        return
    
    running = True
    while running:
        try:
            petition = monitor_connection.recv_message()
            if petition == HEALTH_MSG:
                monitor_connection.send_message(str(status.value))
            elif petition == LOCATION_MSG:
                monitor_connection.send_message(location)
            elif petition == CENTRAL_FALLEN_MSG:
                # monitor_connection.send_message("ok")
                status.set_stopped()
            elif petition == CENTRAL_RESTORED_MSG:
                # monitor_connection.send_message("ok")
                status.set_active()
            elif petition.startswith(PRICE_MSG):
                price = float(petition.removeprefix(PRICE_MSG))
        except ClosingConnectionException:
            running = False
            monitor_connection.close()
        except ConnectionClosedException:
            status.set_stopped()
            return
