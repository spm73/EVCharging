import socket
from threading import Thread
from collections.abc import Callable

from stx_etx_connection import STXETXConnection

class MonitorServer:
    MAX_CONNECTIONS = 1
    def __init__(self, ip_addr: str, port_number: int):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((ip_addr, port_number))

    def listen(self):
        self.server.listen(MonitorServer.MAX_CONNECTIONS)
        print("Engine waiting for monitor connection")
        
    def accept(self, client_handler: Callable[[STXETXConnection], None]):
        monitor_socket, _ = self.server.accept()
        connection = STXETXConnection(monitor_socket)
        thread = Thread(
            target=client_handler,
            args=connection
        )
        thread.start()
    
    def close(self):
        self.server.close()

# class MonitorConnection:
#     MAX_CONNECTIONS = 1
#     # HI_MSG = 'hi'.encode()
#     # OK_MSG = 'ok'.encode()
    
#     def __init__(self, ip_addr, port_number):
#         self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#         self.server.bind((ip_addr, port_number))
        
#     def run(self):
#         self.server.listen(MonitorConnection.MAX_CONNECTIONS)
#         print("Engine waiting for monitor connection")
#         try:
#             while True:
#                 monitor, address = self.server.accept()
                
#         except KeyboardInterrupt:
#             print("Closing the engine")
#         finally:
#             self.server.close()
            
#     def listen(self):
#         self.server.listen(MonitorConnection.MAX_CONNECTIONS)
#         print("Engine waiting for monitor connection")
        
#     def accept(self, function: Callable[[socket.socket, None]]):
#         monitor, _ = self.server.accept()
#         thread = Thread(
#             target=function,
#             args=monitor
#         )
#         thread.start()
    
#     def close(self):
#         self.server.close()
            
#     def res_health_status(monitor: socket.socket, health_status: CPStatus):
#         req = monitor.recv(1024).decode()
#         if not req: 
#             raise MonitorNotRespondingException()
        
#         monitor.sendall(health_status.value)
        
            
    # def hi_monitor(self, monitor):
    #     msg = monitor.recv(2)
    #     if not msg:
    #         raise MonitorNotRespondingException()
    #     monitor.sendall(MonitorConnection.HI_MSG)
        
    # def send_ok(self, monitor):
    #     monitor.sendall(MonitorConnection.OK_MSG)
        
    # def stop(self, monitor):
    #     monitor.close()
    #     self.server.close()
    
    # def answer_supplying_request(self, monitor):
    #     # Think how to check is supplying
    #     msg = monitor.recv(1024)
    #     if not msg:
    #         raise MonitorNotRespondingException()
    #     supplying = True
    #     answer = 'A' if supplying else 'N'
    #     monitor.sendall(answer.encode())  
    
    # def send_status(self, monitor):
    #     monitor.sendall(f"{self.data}".encode())        
        
    # def get_request(self, monitor):
    #     request = monitor.recv(1024).decode()
    #     # process request