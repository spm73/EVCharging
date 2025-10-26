from threading import Thread

from central_config import CentralConfig
from monitor_server import MonitorServer
from CChargingPoint import CChargingPoint
from monitor_handler import monitor_handler

def monitor_server_run(config: CentralConfig, cp_list: list[CChargingPoint]):
    monitor_server = MonitorServer(config.ip, config.port)
    monitor_server.listen()
    
    while True:
        monitor_server.accept(monitor_handler) # faltaria pasar la data, que es una instancia de
        # un CChargingPoint para que pueda actualizar el estado del cp

def main():
    config = CentralConfig()
    monitor_server_thread = Thread(
        target=monitor_server_run,
        args=(config, lista_cps) # lista con lo de CChargingPoint
    )
    
    monitor_server_thread.start()


if __name__ == '__main__':
    main()
