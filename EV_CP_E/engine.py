from cp_status import CPStatus
from monitor_connection import MonitorConnection

class Engine:
    def __init__(self, ip_addr, port_number):
        self.status = CPStatus.ACTIVE
        self.monitor_connection = MonitorConnection(ip_addr, port_number)