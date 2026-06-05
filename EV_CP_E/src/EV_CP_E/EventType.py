from enum import Enum, auto


class EventType(Enum):
    # Del Monitor (via socket)
    KEY_RECEIVED         = auto()  # El Monitor nos manda la clave de cifrado
    MONITOR_DISCONNECTED = auto()  # El Monitor se ha desconectado o caído

    # De Central (via Kafka)
    SERVICE_AUTHORIZED   = auto()  # Central autoriza un suministro a un Driver
    STOP_ORDER           = auto()  # Central ordena parar el CP
    RESUME_ORDER         = auto()  # Central ordena reanudar el CP

    # Del usuario (via menú / Textual)
    SUPPLY_STARTED       = auto()  # El usuario simula que enchufa el vehículo
    SUPPLY_ENDED         = auto()  # El usuario simula que desenchufa el vehículo
    FAULT_SIMULATED      = auto()  # El usuario activa el KO del Engine
    FAULT_RESOLVED       = auto()  # El usuario resuelve el KO del Engine
    VEHICLE_PLUGGED      = auto()  # El conductor empieza la carga tras recibir autorización
    AUTHORIZATION_TIMEOUT= auto()  # Pasan 5 segundos sin que el usuario pulse Start Supply

    # Del sistema (apagado)
    SHUTDOWN             = auto()  # Cierre ordenado del Engine (SIGINT)
