from dataclasses import dataclass, field
from typing import Any

from .EventType import EventType


@dataclass
class Event:
    type: EventType
    payload: Any = field(default=None)

    def __str__(self) -> str:
        if self.payload is not None:
            return f"Event({self.type.name}, payload={self.payload})"
        return f"Event({self.type.name})"
