import socket

class MonitorConnection:
    MAX_CONNECTIONS = 5
    HI_MSG = 'hi'.encode()
    OK_MSG = 'ok'.encode()
    
    def __init__(self, ip_addr, port_number, engine_data):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ip_addr, port_number))
        self.data = engine_data
        
    def run(self):
        self.server.listen(MonitorConnection.MAX_CONNECTIONS)
        print("Engine waiting for monitor connection")
        try:
            while True:
                monitor, address = self.server.accept()
                
        except KeyboardInterrupt:
            print("Closing the engine")
        finally:
            self.server.close()
            
    def hi_monitor(self, monitor):
        msg = monitor.recv(2)
        if not msg:
            # close connection?
            pass
        monitor.sendall(MonitorConnection.HI_MSG)
        
    def send_ok(self, monitor):
        monitor.sendall(MonitorConnection.OK_MSG)
        
    def stop(self, monitor):
        monitor.close()
        self.server.close()
    
    def answer_supplying_request(self, monitor):
        # Think how to check is supplying
        msg = monitor.recv(1024)
        if not msg:
            # close connection?
            pass
        supplying = True
        answer = 'A' if supplying else 'N'
        monitor.sendall(answer.encode())  
    
    def send_status(self, monitor):
        monitor.sendall(f"{self.data}".encode())        
        
    def get_request(self, monitor):
        request = monitor.recv(1024).decode()
        # process request