from communications.sockets import SocketConnection, MessageHandler
from decimal import Decimal

from EV_CP_E.Event import Event
from EV_CP_E.EventType import EventType
from EV_CP_E.CPEngine import CPEngine


def on_config(msg: str) -> str:
    parts = msg.split('#')
    if len(parts) >= 4:
        cp_id_str = parts[1]
        key_str = parts[2]
        price_str = parts[3]
        CPEngine().set_cp_id(cp_id_str)
        CPEngine().set_cipher_key(key_str.encode())
        CPEngine().set_price_per_kwh(Decimal(price_str))
        
        CPEngine().put_event(Event(EventType.KEY_RECEIVED))
        return "CONFIG#copy"
    return "NACK"

def on_status(msg: str) -> str:
    engine = CPEngine()
    state_name = str(engine.current_state)
    
    if "WaitingForConfig" in state_name:
        status = "Disconnected"
    elif getattr(engine, 'fault_simulated', False) or "Broken" in state_name:
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
    handler.register("CONFIG", on_config)
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

