from json import dumps, loads
from typing import Self

from communications.kafka import Message

class StartSupplyMessage(Message):
    def __init__(self, supply_id: int) -> None:
        super().__init__()
        self.supply_id = supply_id
        
    def to_payload(self) -> str:
        return dumps({
            "supply_id": self.supply_id
        })
        
    @classmethod
    def from_payload(cls, payload: str) -> Self:
        json_dict = loads(payload)
        supply_id = json_dict['supply_id']
        
        return cls(supply_id)