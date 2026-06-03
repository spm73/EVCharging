from typing import TYPE_CHECKING
from ..State import State
from ..EventType import EventType
from . import IdleState

if TYPE_CHECKING:
    from ..CPEngine import CPEngine
    from ..Event import Event

class WaitingForKeyState(State):
    """
    Initial and recovery state.
    The Engine cannot do anything until the Monitor connects and sends the KEY.
    """

    def on_enter(self, context: 'CPEngine') -> None:
        context.clear_cipher_key()

    def handle(self, event: 'Event', context: 'CPEngine') -> None:
        if event.event_type == EventType.KEY_RECEIVED:
            context.transition_to(IdleState.IdleState())
        elif event.event_type == EventType.MONITOR_DISCONNECTED:
            pass # Ignore, already waiting
