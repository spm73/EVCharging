from stx_etx_connection import STXETXConnection
from connection_closed_exception import ConnectionClosedException
from closing_connection_exception import ClosingConnectionException
from cp_status import CPStatus

HEALTH_MSG = "req-health-status"
CP_ID_MSG = "cp-id"

def monitor_handler(monitor_connection: STXETXConnection, status: CPStatus, cp_id: str):
    try:
        monitor_connection.enq_answer()
        if status == CPStatus.STOPPED:
            status = CPStatus.ACTIVE
    except ConnectionClosedException:
        status = CPStatus.STOPPED
        return
    
    running = True
    while running:
        try:
            petition = monitor_connection.recv_message()
            if petition == CP_ID_MSG:
                monitor_connection.send_message(str(status.value))
            elif petition == HEALTH_MSG:
                monitor_connection.send_message(cp_id)
        except ClosingConnectionException:
            running = False
            monitor_connection.close()
        except ConnectionClosedException:
            status = CPStatus.STOPPED
            return
