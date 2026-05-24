from json import dumps, loads
from typing import Self

from communications.kafka import Message

class SupplyRequestMessage(Message):
    def __init__(self, driver_id: str, cp_id: str, ip: str) -> None:
        super().__init__()
        self.driver_id = driver_id
        self.cp_id = cp_id
        self.ip = ip
        
    def to_payload(self) -> str:
        return dumps({
            "driver_id": self.driver_id,
            "cp_id": self.cp_id,
            "ip": self.ip
        })
        
    @classmethod
    def from_payload(cls, payload: str) -> Self:
        json_dict = loads(payload)
        driver_id = json_dict['driver_id']
        cp_id = json_dict['cp_id']
        ip = json_dict['ip']
        return cls(driver_id, cp_id, ip)