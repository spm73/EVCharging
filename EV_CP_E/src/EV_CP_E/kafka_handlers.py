from .Event import Event
from .EventType import EventType
from .kafka.messages.EncryptedMessage import EncryptedMessage
from .kafka.messages.CentralCommandMessage import CentralCommandMessage
from .kafka.messages.StartSupplyMessage import StartSupplyMessage
from .CPEngine import CPEngine

def handle_start_supply(message: StartSupplyMessage) -> None:
    """Handler for the cp.start-supply topic."""
    CPEngine().put_event(Event(EventType.SERVICE_AUTHORIZED, str(message.supply_id)))

def handle_central_command(message: CentralCommandMessage) -> None:
    """Handler for the cp.commands topic."""
    if message.action == "stop":
        CPEngine().put_event(Event(EventType.STOP_ORDER))
    elif message.action == "resume":
        CPEngine().put_event(Event(EventType.RESUME_ORDER))

def handle_encrypted_message(enc_message: EncryptedMessage) -> None:
    """
    Decapsulates the encrypted message and dispatches it to the 
    corresponding handler based on its subtype.
    """
    inner_msg = enc_message.message
    
    if isinstance(inner_msg, StartSupplyMessage):
        handle_start_supply(inner_msg)
    elif isinstance(inner_msg, CentralCommandMessage):
        handle_central_command(inner_msg)
