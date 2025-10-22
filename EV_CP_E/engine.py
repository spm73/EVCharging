from cp_status import CPStatus
from monitor_server import MonitorServer

class Engine:
    def __init__(self, ip_addr, port_number):
        self.status = CPStatus.ACTIVE
        self.monitor_connection = MonitorServer(ip_addr, port_number)