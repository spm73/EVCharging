from typing import TYPE_CHECKING
from EV_CP_E.State import State
from EV_CP_E.EventType import EventType
from EV_CP_E.states import IdleState, BrokenState, WaitingForConfigState

if TYPE_CHECKING:
    from EV_CP_E.CPEngine import CPEngine
    from EV_CP_E.Event import Event

class StoppedState(State):
    """
    "Out of Service" via Central's command (e.g., freezing temperatures).
    """

    def handle(self, event: 'Event', context: 'CPEngine') -> None:
        if event.event_type == EventType.RESUME_ORDER or event.event_type == EventType.KEY_RECEIVED:
            context.transition_to(IdleState.IdleState())
            
        elif event.event_type == EventType.FAULT_SIMULATED:
            context.transition_to(BrokenState.BrokenState())
            
        elif event.event_type == EventType.MONITOR_DISCONNECTED:
            context.transition_to(WaitingForConfigState.WaitingForConfigState())
