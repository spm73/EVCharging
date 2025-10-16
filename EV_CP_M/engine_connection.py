import socket

from engine_not_responding_exception import EngineNotRespondingException
from cp_status import CPStatus

class EngineConnection:
    HEALTH_MSG = "req-health-status".encode()
    # IS_SUPPLYING_MSG = "is-supplying".encode()
    # HI_MSG = "hi".encode()
    # WAIT_CENTRAL_MSG = "wait-central".encode()
    # CENTRAL_UNREACHABLE_MSG = "central-unreachable".encode()
    
    def __init__(self, ip_addr, port_number):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip_addr, port_number))
        
    def req_health_status(self) -> CPStatus:
        self.connection.sendall(EngineConnection.HEALTH_MSG)
        health_status = int(self.connection.recv(1).decode())
        if not health_status:
            raise EngineNotRespondingException()
        
        return CPStatus(health_status)
        
    # def hi_engine(self):
    #     self.connection.sendall(EngineConnection.HI_MSG)
    #     answer = self.connection.recv(2).decode()
    #     return bool(answer)
    
    # def wait_engine(self):
    #     self.connection.sendall(EngineConnection.WAIT_CENTRAL_MSG)
    #     answer = self.connection.recv(2).decode()
    #     if not answer:
    #         raise EngineNotRespondingException()
        
    # def central_unreachable(self):
    #     self.connection.sendall(EngineConnection.CENTRAL_UNREACHABLE_MSG)
    #     answer = self.connection.recv(2).decode()
    #     # does not matter if no answer
    #     self.connection.close()
    
    # def is_supplying(self):
    #     self.connection.sendall(EngineConnection.IS_SUPPLYING_MSG)
    #     answer = self.connection.recv(1).decode()
    #     if not answer:
    #         raise EngineNotRespondingException()
    #     return answer == "A" # A for affirm, N for negative
    
    # def request_status(self):
    #     self.connection.sendall(EngineConnection.HEALTH_MSG)
    #     answer = self.connection.recv(1024).decode()
    #     if not answer:
    #         raise EngineNotRespondingException()
    #         # self.msg.send_ko() ## very important
    #     self.msg.update(answer)