from EV_CP_E.Event import Event
from EV_CP_E.EventType import EventType
from EV_CP_E.kafka.messages.EncryptedMessage import EncryptedMessage
from EV_CP_E.kafka.messages.CentralCommandMessage import CentralCommandMessage
from EV_CP_E.kafka.messages.StartSupplyMessage import StartSupplyMessage
from EV_CP_E.CPEngine import CPEngine

def handle_start_supply(message: StartSupplyMessage) -> None:
    """Handler for the cp.start-supply topic."""
    CPEngine().put_event(Event(EventType.SERVICE_AUTHORIZED, str(message.supply_id)))

def handle_central_command(message: CentralCommandMessage) -> None:
    """Handler for the cp.commands topic."""
    if message.action == "stop":
        CPEngine().put_event(Event(EventType.STOP_ORDER))
    elif message.action == "resume":
        CPEngine().put_event(Event(EventType.RESUME_ORDER))


def handle_encrypted_start(message: EncryptedMessage) -> None:
    handle_start_supply(message.message)
    

def handle_encrypted_command(message: EncryptedMessage) -> None:
    handle_central_command(message.message)