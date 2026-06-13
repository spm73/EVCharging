from typing import TYPE_CHECKING
from EV_CP_E.State import State
from EV_CP_E.EventType import EventType
from EV_CP_E.CheckpointManager import CheckpointManager
from EV_CP_E.SupplyData import SupplyData
from EV_CP_E.states import BrokenState, SupplyingState, StoppedState, WaitingForConfigState

if TYPE_CHECKING:
    from EV_CP_E.CPEngine import CPEngine
    from EV_CP_E.Event import Event

class IdleState(State):
    """
    Operational, waiting for a driver to be authorized.
    """

    def on_enter(self, context: 'CPEngine') -> None:
        if context.just_restarted:
            checkpoint_data = CheckpointManager().load()
            if checkpoint_data:
                has_pending = context.restore_from_checkpoint(checkpoint_data)
                if has_pending:
                    # Nos hemos levantado de una caída con un suministro a medias.
                    # Como ya estamos en IdleState, lo terminamos aquí.
                    context.send_final_ticket()
                    context.current_supply = None
                    CheckpointManager().clear()
            context.just_restarted = False

    def handle(self, event: 'Event', context: 'CPEngine') -> None:
        if event.event_type == EventType.SUPPLY_STARTED:
            print("[IdleState] Physical simulation of card reading. Requesting supply from Central...")
            context.request_supply()
            
        elif event.event_type == EventType.SERVICE_AUTHORIZED:
            context.current_supply = SupplyData(supply_id=int(event.payload))
            context.authorization_pending = True
            context.start_authorization_timer()
            
        elif event.event_type == EventType.VEHICLE_PLUGGED:
            if context.authorization_pending:
                context.cancel_authorization_timer()
                context.authorization_pending = False
                context.transition_to(SupplyingState.SupplyingState())
                
        elif event.event_type == EventType.AUTHORIZATION_TIMEOUT:
            if context.authorization_pending:
                print("[IdleState] Timeout: User did not plug in the vehicle in time.")
                context.authorization_pending = False
                context.current_supply = None
            
        elif event.event_type == EventType.STOP_ORDER:
            context.transition_to(StoppedState.StoppedState())
            
        elif event.event_type == EventType.FAULT_SIMULATED:
            context.transition_to(BrokenState.BrokenState())
            
        elif event.event_type == EventType.MONITOR_DISCONNECTED:
            context.transition_to(WaitingForConfigState.WaitingForConfigState())
