from threading import Thread

from central_config import CentralConfig
from monitor_server import MonitorServer
from CChargingPoint import CChargingPoint
from monitor_handler import monitor_handler

def monitor_server_run(config: CentralConfig, cp_list: list[CChargingPoint]):
    monitor_server = MonitorServer(config.ip, config.port)
    monitor_server.listen()
    
    while True:
        monitor_server.accept(monitor_handler) # faltaria pasar la data

def main():
    config = CentralConfig()
    pass


if __name__ == '__main__':
    main()
