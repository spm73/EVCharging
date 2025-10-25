from monitor_config import MonitorConfig
from cp_status import CPStatus
from central_connection import CentralConnection
from engine_connection import EngineConnection
from connection_closed_exception import ConnectionClosedException

def main():
    monitor_config = MonitorConfig()
    central_connection = CentralConnection(monitor_config.central_ip, monitor_config.central_port)
    engine_connection = EngineConnection(monitor_config.engine_ip, monitor_config.engine_port)
    cp_status = CPStatus()

    central_connection.start_connection()
    central_working = True
    engine_connection.start_connection()

    if not central_connection.authorize(monitor_config.cp_ip):
        print("Authorization went wrong, trying to register CP")
        location = engine_connection.req_location()
        if not central_connection.register(monitor_config.cp_ip, location):
            print("Registration went wrong, closing CP")
            return
    
    running = True
    while running:
        try:
            engine_connection.req_health_status(cp_status)
        except ConnectionClosedException:
            cp_status.set_broken_down()
            engine_connection.close_connection()
            # probar a reconectar con monitor antes de cerrar?
            central_connection.close_connection()
            return

        if central_working:
            try:
                central_connection.send_status_message(cp_status)
            except ConnectionClosedException:
                central_connection.close_connection()
                central_working = False # hay que seguir con el suministro


if __name__ == '__main__':
    main()
