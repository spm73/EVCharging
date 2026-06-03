import json
import queue
import threading
from decimal import Decimal
from pathlib import Path
from typing import TYPE_CHECKING

from .Event import Event
from .EventType import EventType
from .SupplyData import SupplyData
from .kafka.messages.EncryptedMessage import EncryptedMessage
from .kafka.messages.SupplyTelemetryMessage import SupplyTelemetryMessage
from .telemetry_thread import TelemetryThread
from .states.WaitingForConfigState import WaitingForConfigState
from .kafka_handlers import handle_encrypted_message

if TYPE_CHECKING:
    from .State import State


class CPEngine:
    """
    Contexto principal de la máquina de estados (Singleton).
    Centraliza la configuración, la clave simétrica y la cola de eventos.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, cp_id: str = None, price_per_kwh: float = None):
        if getattr(self, '_initialized', False):
            return
        self._initialized = True
        
        self.cp_id = cp_id
        self.price_per_kwh = price_per_kwh
        
        self.__current_state: 'State' = WaitingForConfigState()
        
        self.__event_queue: queue.Queue[Event] = queue.Queue()
        self.fault_simulated = False        # Flag: el usuario ha activado el KO

        # --- Datos del suministro en curso ---
        self.current_supply: SupplyData | None = None

        # --- Estado de la máquina ---
        self.pending_stop    = False

        # --- Clave de cifrado (recibida del Monitor, nunca persiste en disco) ---
        self.__cipher_key: bytes | None = None
        self.__cipher_key_lock          = threading.Lock()

        # --- Cola interna de eventos (thread-safe) ---
        self.__event_queue: queue.Queue[Event] = queue.Queue()

        # --- Hilo de telemetría (creado/destruido dinámicamente) ---
        self.__telemetry_thread: threading.Thread | None = None
        self.__telemetry_stop   = threading.Event()

        # --- Estado inicial: siempre arranca esperando la clave ---
        self.__current_state: 'State' = WaitingForConfigState()
        
        # Consumidores de Kafka (se inician dinámicamente)
        self.__start_supply_consumer = None
        self.__commands_consumer = None
        
        self.__current_state.on_enter(self)
        
        self.price_per_kwh: Decimal = Decimal('0.0')

    # -------------------------------------------------------------------------
    # Máquina de estados
    # -------------------------------------------------------------------------

    def transition_to(self, new_state: 'State') -> None:
        print(f"[CPEngine] {self.__current_state} -> {new_state}")
        self.__current_state.on_exit(self)
        self.__current_state = new_state
        self.__current_state.on_enter(self)

    def handle_next_event(self) -> bool:
        """Saca el siguiente evento de la cola (bloqueante) y lo procesa.
        Devuelve False si el evento es SHUTDOWN, True en caso contrario."""
        event = self.__event_queue.get(block=True)
        if event.event_type == EventType.SHUTDOWN:
            print("[CPEngine] SHUTDOWN event received. Stopping event loop.")
            return False
            
        print(f"[CPEngine] Processing {event}")
        self.__current_state.handle(event, self)
        return True

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
            
        EncryptedMessage.set_cipher_key(key)

    def get_cipher_key(self) -> bytes | None:
        with self.__cipher_key_lock:
            return self.__cipher_key

    def clear_cipher_key(self) -> None:
        with self.__cipher_key_lock:
            self.__cipher_key = None
            
        EncryptedMessage.set_cipher_key(None)

    # -------------------------------------------------------------------------
    # Extracción de datos para el Checkpoint
    # -------------------------------------------------------------------------

    def get_checkpoint_data(self) -> dict:
        """Devuelve el estado actual para que el TelemetryThread lo persista."""
        return {
            'state':        str(self.__current_state),
            'pending_stop':  self.pending_stop,
            'supply':       self.current_supply.to_dict() if self.current_supply else None,
        }

    def restore_from_checkpoint(self, data: dict) -> bool:
        """
        Restaura el estado interno a partir de datos del CheckpointManager.
        Devuelve True si había un suministro incompleto pendiente de reportar.
        """
        self.pending_stop = data.get('pending_stop', False)
        supply_data       = data.get('supply')
        
        if supply_data:
            self.current_supply = SupplyData.from_dict(supply_data)
            print(f"[CPEngine] Checkpoint restored: pending supply from {self.current_supply.driver_id}")
            return True
            
        return False

    def has_pending_supply(self) -> bool:
        """True si hay un suministro incompleto restaurado del checkpoint."""
        return self.current_supply is not None

    # -------------------------------------------------------------------------
    # Fachadas de infraestructura (T4-T6 las implementarán)
    # -------------------------------------------------------------------------

    def set_kafka_factory(self, factory) -> None:
        self.kafka_factory = factory

    def set_price_per_kwh(self, price: Decimal) -> None:
        self.price_per_kwh = price

    def set_cp_id(self, cp_id: str) -> None:
        self.cp_id = cp_id

    def __send_telemetry_message(self, msg: SupplyTelemetryMessage) -> None:
        """Lógica común para empaquetar, cifrar y enviar un mensaje al tópico supply.telemetry.cp."""
        if not getattr(self, 'kafka_factory', None):
            return
            
        key = self.get_cipher_key()
        if not key:
            return
            
        enc_msg = EncryptedMessage(self.cp_id, msg)
        
        if not getattr(self, '_CPEngine__telemetry_producer', None):
            self.__telemetry_producer = self.kafka_factory.create_producer('supply.telemetry.cp')
            
        self.__telemetry_producer.send_message(enc_msg)

    def send_telemetry(self) -> None:
        """Envía los datos de telemetría del suministro en curso por Kafka (cifrado)."""
        if not self.current_supply:
            return
            
        msg = SupplyTelemetryMessage(
            msg_type="supplying",
            supply_id=self.current_supply.supply_id,
            price=self.current_supply.amount_accumulated,
            consumption=self.current_supply.kwh_accumulated
        )
        self.__send_telemetry_message(msg)

    def send_final_ticket(self) -> None:
        """Envía el ticket final del suministro a Central por Kafka."""
        if not self.current_supply:
            return
            
        msg = SupplyTelemetryMessage(
            msg_type="ticket",
            supply_id=self.current_supply.supply_id,
            price=self.current_supply.amount_accumulated,
            consumption=self.current_supply.kwh_accumulated
        )
        self.__send_telemetry_message(msg)

    def send_status_update(self, status: str) -> None:
        """Notifica a Central el nuevo estado del CP por Kafka."""
        pass

    def start_telemetry(self) -> None:
        """Arranca el hilo de telemetría. Llamado desde SupplyingState.on_enter()."""
        if getattr(self, '_CPEngine__telemetry_thread', None) and self.__telemetry_thread.is_alive():
            return
        self.__telemetry_thread = TelemetryThread()
        self.__telemetry_thread.start()

    def stop_telemetry(self) -> None:
        """Para el hilo de telemetría. Llamado desde SupplyingState.on_exit()."""
        if getattr(self, '_CPEngine__telemetry_thread', None):
            self.__telemetry_thread.stop()
            self.__telemetry_thread.join(timeout=2.0)
            self.__telemetry_thread = None

    def start_kafka_consumers(self) -> None:
        """Inicia los consumidores de Kafka una vez que tenemos el cp_id."""
        if not self.kafka_factory or not self.cp_id:
            return

        def cp_id_filter(msg: EncryptedMessage) -> bool:
            return self.cp_id is not None and msg.cp_id == self.cp_id

        if not self.__start_supply_consumer:
            self.__start_supply_consumer = self.kafka_factory.create_consumer(
                topic="cp.start-supply",
                group_id=self.cp_id, 
                message_class=EncryptedMessage,
                filter_func=cp_id_filter
            )
            self.__start_supply_consumer.get_notifier().register(handle_encrypted_message)
            self.__start_supply_consumer.start_polling()

        if not self.__commands_consumer:
            self.__commands_consumer = self.kafka_factory.create_consumer(
                topic="cp.commands",
                group_id=self.cp_id, 
                message_class=EncryptedMessage,
                filter_func=cp_id_filter
            )
            self.__commands_consumer.get_notifier().register(handle_encrypted_message)
            self.__commands_consumer.start_polling()

    def stop_kafka_consumers(self) -> None:
        """Detiene los consumidores de Kafka."""
        if self.__start_supply_consumer:
            self.__start_supply_consumer.stop_polling()
            self.__start_supply_consumer = None
            
        if self.__commands_consumer:
            self.__commands_consumer.stop_polling()
            self.__commands_consumer = None
