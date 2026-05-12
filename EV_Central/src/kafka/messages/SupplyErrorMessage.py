from json import dumps, loads
from communications.kafka import Message
from typing import Self

class SupplyRequestNotificationMessage(Message):
    def __init__(self, driver_id: str, error_msg: str) -> None:
        super().__init__()
        self.driver_id = driver_id
        self.error_msg = error_msg
        
    def to_payload(self) -> str:
        return dumps({
            "to": self.driver_id,
            "error_msg": self.error_msg
        })
        
    @classmethod
    def from_payload(cls, payload: str) -> Self:
        json_dict = loads(payload)
        driver_id = json_dict['to']
        error_msg = json_dict['error_msg']
        return cls(driver_id, error_msg)