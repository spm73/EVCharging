from communications.sockets import SocketConnection

from .make_handler import make_handler

def handle_monitor(connection: SocketConnection) -> None:
    handler = make_handler()
    
    while True:
        message = connection.receive()
        if message is None:
            break
        
        response = handler.handle(message)
        if response:
            connection.send(response)
            if response.startswith("BYE"):
                break