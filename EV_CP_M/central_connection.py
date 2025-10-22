import socket

from central_not_responding_exception import CentralNotRespondingException
from cp_status import CPStatus

class CentralConnection:
    WAITING_SUPPLY_MSG = 'wait-supply'.encode()
    REGISTER_MSG = 'REG'.encode()
    AUTH_MSG = 'AUTH'.encode()
    
    def __init__(self, ip_addr, port_number):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip_addr, port_number))
        
    def authorize(self, cp_id: str) -> bool:
        self.connection.sendall(cp_id.encode())
        answer = self.connection.recv(3).decode()
        if not answer:
            raise CentralNotRespondingException()
        return answer != "BAD"
        
    def register(self, cp_id: str, street: str):
        self.connection.sendall(CentralConnection.REGISTER_MSG)
        answer = self.connection.recv(3).decode()
        if not answer:
            raise CentralNotRespondingException()
        
        
    def send_status_message(self, current_status: CPStatus):
        self.connection.sendall(current_status.value)
        answer = self.connection.recv(3).decode()
        if not answer:    
            raise CentralNotRespondingException()
      
    # def waiting_supply(self): 
    #     self.connection.sendall(CentralConnection.WAITING_SUPPLY_MSG)
    #     answer = self.connection.recv(2).decode()
    #     if not answer:
    #         raise CentralNotRespondingException()
        
        
    # def run(self, engine_id):
    #     if not self.authorize(engine_id):
    #         return
        
    #     # mientras que no de un mensaje ko o acabado
        