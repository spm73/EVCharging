from typing import TYPE_CHECKING
from EV_CP_E.State import State
from EV_CP_E.EventType import EventType
from EV_CP_E.CheckpointManager import CheckpointManager
from EV_CP_E.states import StoppedState, IdleState, BrokenState, WaitingForConfigState

if TYPE_CHECKING:
    from EV_CP_E.CPEngine import CPEngine
    from EV_CP_E.Event import Event

class SupplyingState(State):
    """
    Vehicle connected and actively charging.
    """

    def on_enter(self, context: 'CPEngine') -> None:
        context.start_telemetry()

    def on_exit(self, context: 'CPEngine') -> None:
        context.stop_telemetry()
        
        # Only clear supply if transitioning due to SUPPLY_ENDED or FAULT_SIMULATED.
        # If we just transition to WaitingForKey (disconnect), we leave it so it can be recovered.
        if not context.fault_simulated and context.current_supply:
            # We don't send final ticket here for fault_simulated because BrokenState handles it
            pass

    def handle(self, event: 'Event', context: 'CPEngine') -> None:
        if event.event_type == EventType.SUPPLY_ENDED:
            context.send_final_ticket()
            context.current_supply = None
            CheckpointManager().clear()
            
            if context.pending_stop:
                context.pending_stop = False
                context.transition_to(StoppedState.StoppedState())
            else:
                context.transition_to(IdleState.IdleState())
                
        elif event.event_type == EventType.STOP_ORDER:
            context.pending_stop = True
            
        elif event.event_type == EventType.FAULT_SIMULATED:
            context.transition_to(BrokenState.BrokenState())
            
        elif event.event_type == EventType.MONITOR_DISCONNECTED:
            context.transition_to(WaitingForConfigState.WaitingForConfigState())
