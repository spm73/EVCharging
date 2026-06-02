from communications.sockets import SocketConnection, MessageHandler
from .Event import Event
from .EventType import EventType
from .CPEngine import CPEngine


def on_key(msg: str) -> str:
    parts = msg.split('#')
    if len(parts) >= 2:
        key_str = parts[1]
        CPEngine().set_cipher_key(key_str.encode())
        CPEngine().put_event(Event(EventType.KEY_RECEIVED))
        return "KEY#copy"
    return "NACK"

def on_status(msg: str) -> str:
    engine = CPEngine()
    state_name = str(engine.current_state)
    
    if "WaitingForKey" in state_name:
        status = "Disconnected"
    elif engine.fault_simulated or "Broken" in state_name:
        status = "Broken Down"
    elif "Supplying" in state_name:
        status = "Supplying"
    elif "Stopped" in state_name:
        status = "Stopped"
    else:
        status = "Active"
        
    return f"STATUS#{status}"
    
def on_out_of_service(msg: str) -> str:
    CPEngine().put_event(Event(EventType.STOP_ORDER))
    return "OUT_OF_SERVICE#copy"


def create_monitor_msg_handler() -> MessageHandler:
    handler = MessageHandler(default=lambda x: "NACK")
    handler.register("KEY", on_key)
    handler.register("STATUS", on_status)
    handler.register("OUT_OF_SERVICE", on_out_of_service)
    return handler

def socket_handler(connection: SocketConnection):
    msg_handler = create_monitor_msg_handler()
    try:
        while True:
            msg = connection.receive()
            if not msg:
                break
            response = msg_handler.handle(msg)
            if response:
                connection.send(response)
    except Exception as e:
        print(f"[MonitorSocket] Error/Disconnect: {e}")
    finally:
        CPEngine().clear_cipher_key()
        CPEngine().put_event(Event(EventType.MONITOR_DISCONNECTED))

