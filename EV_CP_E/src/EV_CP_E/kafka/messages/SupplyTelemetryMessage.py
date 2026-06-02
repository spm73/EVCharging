from json import dumps, loads
from typing import Self

from communications.kafka import Message

class SupplyTelemetryMessage(Message):
    def __init__(self, cp_id: str, kwh_consumed: float, price_per_kwh: float, driver_id: str) -> None:
        super().__init__()
        self.cp_id = cp_id
        self.kwh_consumed = kwh_consumed
        self.price_per_kwh = price_per_kwh
        self.driver_id = driver_id
        
    def to_payload(self) -> str:
        return dumps({
            "cp_id": self.cp_id,
            "kwh_consumed": self.kwh_consumed,
            "price_per_kwh": self.price_per_kwh,
            "driver_id": self.driver_id
        })
        
    @classmethod
    def from_payload(cls, payload: str) -> Self:
        json_dict = loads(payload)
        return cls(
            json_dict['cp_id'],
            json_dict['kwh_consumed'],
            json_dict['price_per_kwh'],
            json_dict['driver_id']
        )
