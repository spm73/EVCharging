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
    engine_connection.start_connection(monitor_config.cp_ip)
    price = None

    try:
        auth_answer = central_connection.authorize(monitor_config.cp_ip)
        if auth_answer['status'] != 'authorized':
            print("Authorization went wrong, trying to register CP")
            location = engine_connection.req_location()
            print(location)
            reg_answer = central_connection.register(monitor_config.cp_ip, location)
            print(reg_answer)
            if reg_answer['status'] != 'registered':
                print("Registration went wrong, closing CP")
                engine_connection.close_connection()
                central_connection.close_connection()
                return
            else:
                price = reg_answer['price']
        else:
            price = auth_answer['price']
    except ConnectionClosedException:
        print("Central has fallen and authentication process could not be carried out")
        central_working = False
        engine_connection.send_central_fallen()
        # reconectar?
        engine_connection.close_connection()
        central_connection.close_connection()
        return
        
    try:
        engine_connection.send_price(price)
    except ConnectionClosedException:
        engine_connection.close_connection()    
        central_connection.close_connection()
        return
    
    running = True
    while running:
        try:
            engine_connection.req_health_status(cp_status)
        except ConnectionClosedException:
            cp_status.set_broken_down()
            engine_connection.close_connection()
            try:
                central_connection.send_status_message(cp_status)
            except ConnectionClosedException:
                central_connection.close_connection()
                central_working = False
                return
            # probar a reconectar con engine antes de cerrar?
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
