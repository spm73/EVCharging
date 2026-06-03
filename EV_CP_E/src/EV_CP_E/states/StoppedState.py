from typing import TYPE_CHECKING
from ..State import State
from ..EventType import EventType
from . import IdleState, BrokenState, WaitingForKeyState

if TYPE_CHECKING:
    from ..CPEngine import CPEngine
    from ..Event import Event

class StoppedState(State):
    """
    "Out of Service" via Central's command (e.g., freezing temperatures).
    """

    def handle(self, event: 'Event', context: 'CPEngine') -> None:
        if event.event_type == EventType.RESUME_ORDER:
            context.transition_to(IdleState.IdleState())
            
        elif event.event_type == EventType.FAULT_SIMULATED:
            context.transition_to(BrokenState.BrokenState())
            
        elif event.event_type == EventType.MONITOR_DISCONNECTED:
            context.transition_to(WaitingForKeyState.WaitingForKeyState())
