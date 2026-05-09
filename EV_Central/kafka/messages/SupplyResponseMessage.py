from json import dumps, loads
from typing import Self

from communications.kafka import Message

class SupplyResponseMessage(Message):
    def __init__(
        self, 
        driver_id: str, 
        status: str, 
        reason: str | None, 
        supply_id: str | None
        ) -> None:
        super().__init__()
        self.driver_id = driver_id
        self.status = status
        self.reason = reason
        self.supply_id = supply_id
        
    def to_payload(self) -> str:
        return dumps({
            "driver_id": self.driver_id,
            "status": self.status,
            "reason": self.reason,
            "supply_id": self.supply_id
        })
        
    @classmethod
    def from_payload(cls, payload: str) -> Self:
        json_dict = loads(payload)
        driver_id = json_dict['driver_id']
        status = json_dict['status']
        reason = json_dict['reason']
        supply_id = json_dict['supply_id']
        return cls(driver_id, status, reason, supply_id)