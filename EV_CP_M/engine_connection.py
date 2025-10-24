# import socket

from stx_etx_connection import STXETXConnection
from cp_status import CPStatus

class EngineConnection(STXETXConnection):
    HEALTH_MSG = "req-health-status"
    CP_ID_MSG = "cp-id"

    def __init__(self, ip_addr: str, port_number: int):
        super().__init__(ip_addr, port_number)
        
    def start_connection(self):
        self.enq_message()
        
    def close_connection(self):
        self.eot_message()
        
    # def req_health_status(self) -> CPStatus:
    #     self.send_message(EngineConnection.HEALTH_MSG)
    #     status_number = int(self.recv_message())
    #     return CPStatus(status_number)
    
    def req_health_status(self, status: CPStatus):
        self.send_message(EngineConnection.HEALTH_MSG)
        status_number = int(self.recv_message())
        match status_number:
            case 1:
                status.set_active()
            case 2:
                status.set_supplying()
            case 3:
                status.set_stopped()
            case 4:
                status.set_waiting_for_supplying()
            case _:
                status.set_broken_down()
        
    def req_cp_id(self) -> str:
        self.send_message(EngineConnection.CP_ID_MSG)
        cp_id = self.recv_message()
        return cp_id

# class EngineConnection:
#     HEALTH_MSG = "req-health-status".encode()
    # IS_SUPPLYING_MSG = "is-supplying".encode()
    # HI_MSG = "hi".encode()
    # WAIT_CENTRAL_MSG = "wait-central".encode()
    # CENTRAL_UNREACHABLE_MSG = "central-unreachable".encode()
    
    # def __init__(self, ip_addr, port_number):
    #     self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #     self.connection.connect((ip_addr, port_number))
        
    # def req_health_status(self) -> CPStatus:
    #     self.connection.sendall(EngineConnection.HEALTH_MSG)
    #     health_status = int(self.connection.recv(1).decode())
    #     if not health_status:
    #         raise EngineNotRespondingException()
        
    #     return CPStatus(health_status)
        
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