import json
import queue
import threading
from pathlib import Path
from typing import TYPE_CHECKING

from .Event import Event
from .EventType import EventType
from .SupplyData import SupplyData

if TYPE_CHECKING:
    from .State import State


class CPEngine:

    def __init__(
        self,
        cp_id: str,
        price_per_kwh: float,
        checkpoint_path: str = "checkpoint.json",
    ) -> None:
        self.cp_id           = cp_id
        self.price_per_kwh   = price_per_kwh

        # --- Estado de la máquina ---
        self.pending_stop    = False
        self.fault_simulated = False        # Flag: el usuario ha activado el KO

        # --- Datos del suministro en curso ---
        self.current_supply: SupplyData | None = None

        # --- Clave de cifrado (recibida del Monitor, nunca persiste en disco) ---
        self.__cipher_key: bytes | None = None
        self.__cipher_key_lock          = threading.Lock()

        # --- Cola interna de eventos (thread-safe) ---
        self.__event_queue: queue.Queue[Event] = queue.Queue()

        # --- Hilo de telemetría (creado/destruido dinámicamente) ---
        self.__telemetry_thread: threading.Thread | None = None
        self.__telemetry_stop   = threading.Event()

        # --- Checkpoint ---
        self.__checkpoint_path = Path(checkpoint_path)

        # --- Estado inicial: siempre arranca esperando la clave ---
        # La importación aquí evita la circularidad en tiempo de ejecución
        from .states.WaitingForKeyState import WaitingForKeyState
        self.__current_state: 'State' = WaitingForKeyState()
        self.__current_state.on_enter(self)

    # -------------------------------------------------------------------------
    # Máquina de estados
    # -------------------------------------------------------------------------

    def transition_to(self, new_state: 'State') -> None:
        print(f"[CPEngine] {self.__current_state} → {new_state}")
        self.__current_state.on_exit(self)
        self.__current_state = new_state
        self.__current_state.on_enter(self)
        self.save_checkpoint()

    def handle_next_event(self) -> None:
        """Saca el siguiente evento de la cola (bloqueante) y lo procesa."""
        event = self.__event_queue.get(block=True)
        print(f"[CPEngine] Procesando {event}")
        self.__current_state.handle(event, self)

    def put_event(self, event: Event) -> None:
        """Punto de entrada universal para todos los hilos productores."""
        self.__event_queue.put(event)

    @property
    def current_state(self) -> 'State':
        return self.__current_state

    # -------------------------------------------------------------------------
    # Clave de cifrado
    # -------------------------------------------------------------------------

    def set_cipher_key(self, key: bytes) -> None:
        with self.__cipher_key_lock:
            self.__cipher_key = key

    def get_cipher_key(self) -> bytes | None:
        with self.__cipher_key_lock:
            return self.__cipher_key

    def clear_cipher_key(self) -> None:
        with self.__cipher_key_lock:
            self.__cipher_key = None

    # -------------------------------------------------------------------------
    # Checkpoint (T3)
    # -------------------------------------------------------------------------

    def save_checkpoint(self) -> None:
        """Persiste el estado mínimo necesario para recuperarse de una caída."""
        data = {
            'state':        str(self.__current_state),
           'pending_stop':  self.pending_stop,
            'supply':       self.current_supply.to_dict() if self.current_supply else None,
        }
        try:
            self.__checkpoint_path.write_text(json.dumps(data, indent=2))
        except OSError as e:
            print(f"[CPEngine] Error guardando checkpoint: {e}")

    def load_checkpoint(self) -> bool:
        """
        Carga el checkpoint si existe.
        Devuelve True si había datos de un suministro incompleto pendiente de reportar.
        La clave NO se restaura (seguridad): siempre hay que esperar al Monitor.
        """
        if not self.__checkpoint_path.exists():
            return False

        try:
            data = json.loads(self.__checkpoint_path.read_text())
            self.pending_stop = data.get('pending_stop', False)
            supply_data       = data.get('supply')
            if supply_data:
                self.current_supply = SupplyData.from_dict(supply_data)
                print(f"[CPEngine] Checkpoint restaurado: suministro pendiente de {self.current_supply.driver_id}")
                return True
        except (OSError, json.JSONDecodeError, KeyError) as e:
            print(f"[CPEngine] Error leyendo checkpoint: {e}")

        return False

    def clear_checkpoint(self) -> None:
        try:
            self.__checkpoint_path.unlink(missing_ok=True)
        except OSError as e:
            print(f"[CPEngine] Error borrando checkpoint: {e}")

    def has_pending_supply(self) -> bool:
        """True si hay un suministro incompleto restaurado del checkpoint."""
        return self.current_supply is not None

    # -------------------------------------------------------------------------
    # Fachadas de infraestructura (T4-T6 las implementarán)
    # -------------------------------------------------------------------------

    def send_telemetry(self) -> None:
        """Envía los datos de telemetría del suministro en curso por Kafka (cifrado)."""
        raise NotImplementedError

    def send_final_ticket(self) -> None:
        """Envía el ticket final del suministro a Central por Kafka."""
        raise NotImplementedError

    def send_status_update(self, status: str) -> None:
        """Notifica a Central el nuevo estado del CP por Kafka."""
        raise NotImplementedError

    def start_telemetry(self) -> None:
        """Arranca el hilo de telemetría. Llamado desde SupplyingState.on_enter()."""
        raise NotImplementedError

    def stop_telemetry(self) -> None:
        """Para el hilo de telemetría. Llamado desde SupplyingState.on_exit()."""
        raise NotImplementedError
