from json import dumps, loads
from typing import Self, Literal

from communications.kafka import Message

class CentralCommandMessage(Message):
    def __init__(
        self, 
        target: str, 
        action: Literal["stop", "resume", "lock"]
    ) -> None:
        super().__init__()
        self.target = target
        self.action = action
        
    def to_payload(self) -> str:
        return dumps({
            "target": self.target,
            "action": self.action
        })
        
    @classmethod
    def from_payload(cls, payload: str) -> Self:
        json_dict = loads(payload)
        target = json_dict['target']
        action = json_dict['action']
        
        return cls(target, action)