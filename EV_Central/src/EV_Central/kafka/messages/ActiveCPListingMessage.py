from json import dumps, loads
from typing import Self

from communications.kafka import Message

class ActiveCPListingMessage(Message):
    def __init__(self, active_cps: list[str]) -> None:
        super().__init__()
        self.active_cps = active_cps
        
    def to_payload(self) -> str:
        return dumps(self.active_cps)
        
    @classmethod
    def from_payload(cls, payload: str) -> Self:
        active_cps = loads(payload) 
        return cls(active_cps)