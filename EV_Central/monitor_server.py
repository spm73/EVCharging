import socket
import threading

class MonitorServer:
    MAX_CONNECTIONS = 5
    def __init__(self, ip_addr, port_number):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ip_addr, port_number))
        
    def run(self):
        self.server.listen(MonitorServer.MAX_CONNECTIONS)
        print("Server waiting for connections")
        try:
            while True:
                client, address = self.server.accept()
                
                client_thread = threading.Thread(
                    target=self._client_handler,
                    args=(client, address)    
                )
                client_thread.start()
                
        except KeyboardInterrupt:
            print("Closing the monitor server ...")
        finally:
            for active_threads in threading.enumerate():
                active_threads.join()
            self.server.close()
    
    def _client_handler(client_socket, address):
        engine_id = client_socket.recv(1024)
        is_authorized = MonitorServer._authorize(engine_id)
        client_socket.sendall(is_authorized)
        if is_authorized == "BAD":
            return
        
        status_msg = client_socket.recv(1024).decode()
        client_socket.sendall("ACK")
        # update data of cp
        
        
        
    
    @staticmethod
    def _authorize(engine_id) :
        return "OK" # or "BAD"
    