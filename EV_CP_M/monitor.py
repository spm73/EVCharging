from engine_connection import EngineConnection
from central_connection import CentralConnection

class Monitor:
    def __init__(self, engine_ip, engine_port, central_ip, central_port):
        self.engine_connection = EngineConnection(engine_ip, engine_port)
        self.central_connection = CentralConnection(central_ip, central_port)