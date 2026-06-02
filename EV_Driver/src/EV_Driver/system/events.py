from dataclasses import dataclass
from typing import Any

from enum import Enum

# Creamos el Enum con las únicas opciones válidas en tu sistema
class Intention(Enum):
    KEYBOARD_INPUT = "KEYBOARD_INPUT"
    UPDATE_CPS = "UPDATE_CPS"
    NOTIFICATIONS = "NOTIFICATIONS"
    TELEMETRY_INFO = "TELEMETRY_INFO"
    TELEMETRY_TICKET = "TELEMETRY_TICKET"
    ACCEPTED_RESPONSE = "ACCEPTED_RESPONSE"
    DENIED_RESPONSE = "DENIED_RESPONSE"
    KAFKA_ERROR = "KAFKA_ERROR"

@dataclass
class SystemEvent:
    intention: Intention
    data: Any