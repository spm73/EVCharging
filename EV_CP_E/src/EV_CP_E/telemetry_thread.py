import threading
from decimal import Decimal
from .CPEngine import CPEngine
from .CheckpointManager import CheckpointManager

class TelemetryThread(threading.Thread):
    def __init__(self):
        super().__init__(daemon=True)
        self._stop_event = threading.Event()

    def stop(self) -> None:
        self._stop_event.set()

    def run(self) -> None:
        while not self._stop_event.is_set():
            if self._stop_event.wait(1.0):
                break
            
            engine = CPEngine()
            if engine.current_supply:
                engine.current_supply.kwh_accumulated += 1
                
                # amount_accumulated = kwh_accumulated * price_per_kwh
                engine.current_supply.amount_accumulated = Decimal(str(engine.current_supply.kwh_accumulated)) * engine.price_per_kwh
            
            engine.send_telemetry()
            
            # Delega el guardado al CheckpointManager usando los datos del Engine
            checkpoint_data = engine.get_checkpoint_data()
            CheckpointManager().save(checkpoint_data)
