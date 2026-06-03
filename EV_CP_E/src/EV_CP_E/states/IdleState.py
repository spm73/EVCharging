from typing import TYPE_CHECKING
from ..State import State
from ..EventType import EventType
from ..CheckpointManager import CheckpointManager
from ..SupplyData import SupplyData
from . import BrokenState, SupplyingState, StoppedState, WaitingForConfigState

if TYPE_CHECKING:
    from ..CPEngine import CPEngine
    from ..Event import Event

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
            print("[IdleState] Simulación física de lectura de tarjeta. Solicitando suministro a Central...")
            context.request_supply()
            
        elif event.event_type == EventType.SERVICE_AUTHORIZED:
            context.current_supply = SupplyData(supply_id=int(event.payload))
            context.transition_to(SupplyingState.SupplyingState())
            
        elif event.event_type == EventType.STOP_ORDER:
            context.transition_to(StoppedState.StoppedState())
            
        elif event.event_type == EventType.FAULT_SIMULATED:
            context.transition_to(BrokenState.BrokenState())
            
        elif event.event_type == EventType.MONITOR_DISCONNECTED:
            context.transition_to(WaitingForConfigState.WaitingForConfigState())
