import socket

class EngineConnection:
    HEALTH_MSG = "req-health-status".encode()
    def __init__(self, ip_addr, port_number, status_msg):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip_addr, port_number))
        self.msg = status_msg
        
    def request_status(self):
        self.connection.sendall(EngineConnection.HEALTH_MSG)
        answer = self.connection.recv(1024).decode()
        if not answer:
            self.msg.send_ko()
        self.msg.update(answer)
        
        