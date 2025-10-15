import socket

class MonitorConnection:
    MAX_CONNECTIONS = 5
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
            
    def send_status(self, monitor):
        monitor.sendall(f"{self.data}".encode())
            
    def get_request(self, monitor):
        request = monitor.recv(1024).decode()
        # process request