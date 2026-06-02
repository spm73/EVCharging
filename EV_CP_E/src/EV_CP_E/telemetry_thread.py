import threading
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
            
            CPEngine().send_telemetry()
            
            # Delega el guardado al CheckpointManager usando los datos del Engine
            checkpoint_data = CPEngine().get_checkpoint_data()
            CheckpointManager().save(checkpoint_data)
