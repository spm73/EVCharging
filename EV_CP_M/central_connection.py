import socket

class CentralConnection:
    WAITING_SUPPLY_MSG = 'wait-supply'.encode()
    
    def __init__(self, ip_addr, port_number, status_msg):
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip_addr, port_number))
        self.msg = status_msg
        
    def authorize(self, engine_id) -> bool:
        self.connection.sendall(engine_id.encode())
        answer = self.connection.recv(3).decode()
        if not answer:
            pass
        return answer != "BAD"
        
    def send_status_message(self):
        current_status = self.msg.encode()
        self.connection.sendall(current_status)
        answer = self.connection.recv(3).decode()
        if not answer:    
            raise ConnectionError('Server does not answer')
      
    def waiting_supply(self): 
        self.connection.sendall(CentralConnection.WAITING_SUPPLY_MSG)
        answer = self.connection.recv(2).decode()
        if not answer:
            pass
        
        
    # def run(self, engine_id):
    #     if not self.authorize(engine_id):
    #         return
        
    #     # mientras que no de un mensaje ko o acabado
        