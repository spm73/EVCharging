from json import dumps, loads
from typing import Self

from communications.kafka import Message

class SupplyRequestNotificationMessage(Message):
    def __init__(self, driver_id: str, message: str) -> None:
        super().__init__()
        self.driver_id = driver_id
        self.message = message
        
    def to_payload(self) -> str:
        return dumps({
            "to": self.driver_id,
            "message": self.message
        })
        
    @classmethod
    def from_payload(cls, payload: str) -> Self:
        json_dict = loads(payload)
        driver_id = json_dict['to']
        message = json_dict['message']
        return cls(driver_id, message)