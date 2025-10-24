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
    engine_connection.start_connection()

    if not central_connection.authorize(monitor_config.cp_ip):
        print("Could not connect to Central because authorization went wrong")
        return
    
    running = True
    while running:
        try:
            engine_connection.req_health_status(cp_status)
        except ConnectionClosedException:
            cp_status.set_broken_down()
            engine_connection.close_connection()
            central_connection.close_connection()
            return

        try:
            central_connection.send_status_message(cp_status)
        except ConnectionClosedException:
            engine_connection.close_connection()
            central_connection.close_connection()
            running = False
            # que pasa sí central se cae
            # Sergio: parar monitor
            # Nico: cerrar la conexión


if __name__ == '__main__':
    main()
