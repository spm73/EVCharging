from typing import TYPE_CHECKING
from EV_CP_E.State import State
from EV_CP_E.EventType import EventType
from EV_CP_E.states import IdleState

if TYPE_CHECKING:
    from EV_CP_E.CPEngine import CPEngine
    from EV_CP_E.Event import Event

class WaitingForConfigState(State):
    """
    Initial state. The CP is not usable until the Monitor connects
    and sends the configuration (ID, encryption key, and price).
    """

    def on_enter(self, context: 'CPEngine') -> None:
        context.clear_cipher_key()
        context.stop_kafka_consumers()

    def handle(self, event: 'Event', context: 'CPEngine') -> None:
        if event.event_type == EventType.KEY_RECEIVED:
            print("[WaitingForConfigState] Clave, precio e ID recibidos del Monitor.")
            context.start_kafka_consumers()
            context.transition_to(IdleState.IdleState())
        elif event.event_type == EventType.MONITOR_DISCONNECTED:
            pass # Ignore, already waiting
