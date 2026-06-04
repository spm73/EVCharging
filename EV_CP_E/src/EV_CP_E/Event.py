from dataclasses import dataclass, field
from typing import Any

from EV_CP_E.EventType import EventType


@dataclass
class Event:
    event_type: EventType
    payload: Any = field(default=None)

    def __str__(self) -> str:
        if self.payload is not None:
            return f"Event({self.event_type.name}, payload={self.payload})"
        return f"Event({self.event_type.name})"
