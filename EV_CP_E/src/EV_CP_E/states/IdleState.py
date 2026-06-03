from typing import TYPE_CHECKING
from ..State import State
from ..EventType import EventType
from ..CheckpointManager import CheckpointManager
from ..SupplyData import SupplyData
from . import BrokenState, SupplyingState, StoppedState, WaitingForKeyState

if TYPE_CHECKING:
    from ..CPEngine import CPEngine
    from ..Event import Event

class IdleState(State):
    """
    Operational, waiting for a driver to be authorized.
    """

    def on_enter(self, context: 'CPEngine') -> None:
        checkpoint_data = CheckpointManager().load()
        if checkpoint_data:
            has_pending = context.restore_from_checkpoint(checkpoint_data)
            if has_pending:
                context.transition_to(BrokenState.BrokenState())

    def handle(self, event: 'Event', context: 'CPEngine') -> None:
        if event.event_type == EventType.SERVICE_AUTHORIZED:
            context.current_supply = SupplyData(context.cp_id, event.payload)
            context.transition_to(SupplyingState.SupplyingState())
            
        elif event.event_type == EventType.STOP_ORDER:
            context.transition_to(StoppedState.StoppedState())
            
        elif event.event_type == EventType.FAULT_SIMULATED:
            context.transition_to(BrokenState.BrokenState())
            
        elif event.event_type == EventType.MONITOR_DISCONNECTED:
            context.transition_to(WaitingForKeyState.WaitingForKeyState())
