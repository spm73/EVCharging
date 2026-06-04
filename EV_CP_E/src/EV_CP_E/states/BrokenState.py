from typing import TYPE_CHECKING
from EV_CP_E.State import State
from EV_CP_E.EventType import EventType
from EV_CP_E.CheckpointManager import CheckpointManager
from EV_CP_E.states import IdleState, WaitingForConfigState

if TYPE_CHECKING:
    from EV_CP_E.CPEngine import CPEngine
    from EV_CP_E.Event import Event

class BrokenState(State):
    """
    Hardware fault detected or interrupted supply recovered.
    """

    def on_enter(self, context: 'CPEngine') -> None:
        if context.current_supply is not None:
            context.send_final_ticket()
            context.current_supply = None
            CheckpointManager().clear()

    def on_exit(self, context: 'CPEngine') -> None:
        context.fault_simulated = False

    def handle(self, event: 'Event', context: 'CPEngine') -> None:
        if event.event_type == EventType.FAULT_RESOLVED:
            context.transition_to(IdleState.IdleState())
            
        elif event.event_type == EventType.MONITOR_DISCONNECTED:
            context.transition_to(WaitingForConfigState.WaitingForConfigState())
