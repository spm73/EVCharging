from communications.sockets import SocketConnection

from EV_Central.sockets.make_handler import make_handler
from EV_Central.audit.audit import audit
from EV_Central.models.CPStatus import CPStatus

def handle_monitor(connection: SocketConnection) -> None:
    ip = connection.get_peer_ip()
    handler, get_cp = make_handler()
    last_status = None

    while True:
        message = connection.receive()
        if message is None:
            break
        
        action = message.split('#')[0]
        if action == "STATUS":
            description = message.split('#')[1]
            if description != last_status:
                audit(ip, action, description)
                last_status = description
        else:
            description = None
            audit(ip, action, description)
        
        response = handler.handle(message)
        connection.send(response)
        if response.startswith("BYE"):
            break

    # Cuando el bucle termina, el monitor se ha desconectado
    cp = get_cp()
    if cp is not None and cp.get_status() != CPStatus.DISCONNECTED:
        cp.change_status(CPStatus.DISCONNECTED)
        audit(ip, 'DISCONNECT', f"Monitor for CP {cp.get_id()} disconnected unexpectedly")