from typing import TYPE_CHECKING
from ..State import State
from ..EventType import EventType
from ..CheckpointManager import CheckpointManager
from . import IdleState, WaitingForConfigState

if TYPE_CHECKING:
    from ..CPEngine import CPEngine
    from ..Event import Event

class BrokenState(State):
    """
    Hardware fault detected or interrupted supply recovered.
    """

    def on_enter(self, context: 'CPEngine') -> None:
        if context.current_supply is not None:
            context.send_final_ticket()
            context.current_supply = None
            CheckpointManager().clear()

    def handle(self, event: 'Event', context: 'CPEngine') -> None:
        if event.event_type == EventType.FAULT_RESOLVED:
            context.transition_to(IdleState.IdleState())
            
        elif event.event_type == EventType.MONITOR_DISCONNECTED:
            context.transition_to(WaitingForConfigState.WaitingForConfigState())
