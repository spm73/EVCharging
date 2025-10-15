import socket

class EngineConnection:
    HEALTH_MSG = "req-health-status".encode()
    IS_SUPPLYING_MSG = "is-supplying".encode()
    HI_MSG = "hi".encode()
    WAIT_CENTRAL_MSG = "wait-central".encode()
    CENTRAL_UNREACHABLE_MSG = "central-unreachable".encode()
    
    def __init__(self, ip_addr, port_number, status_msg):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip_addr, port_number))
        self.msg = status_msg
        
    def hi_engine(self):
        self.connection.sendall(EngineConnection.HI_MSG)
        answer = self.connection.recv(2).decode()
        return bool(answer)
    
    def wait_engine(self):
        self.connection.sendall(EngineConnection.WAIT_CENTRAL_MSG)
        answer = self.connection.recv(2).decode()
        if not answer:
            pass
        
    def central_unreachable(self):
        self.connection.sendall(EngineConnection.CENTRAL_UNREACHABLE_MSG)
        answer = self.connection.recv(2).decode()
        # does not matter if no answer
        self.connection.close()
    
    def is_supplying(self):
        self.connection.sendall(EngineConnection.IS_SUPPLYING_MSG)
        answer = self.connection.recv(1).decode()
        if not answer:
            pass
        return answer == "A" # A for affirm, N for negative
    
    def request_status(self):
        self.connection.sendall(EngineConnection.HEALTH_MSG)
        answer = self.connection.recv(1024).decode()
        if not answer:
            self.msg.send_ko()
        self.msg.update(answer)