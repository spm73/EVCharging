from communications.sockets import SocketConnection

from .make_handler import make_handler
from ..audit.audit import audit

def handle_monitor(connection: SocketConnection) -> None:
    handler = make_handler()
    ip = connection.get_peer_ip()
    
    while True:
        message = connection.receive()
        if message is None:
            break
        
        action = message.split('#')[0]
        description = None
        if action == "STATUS":
            description = message.split('#')[1]
        audit(ip, action, description)
        
        response = handler.handle(message)
        connection.send(response)
        if response.startswith("BYE"):
            break