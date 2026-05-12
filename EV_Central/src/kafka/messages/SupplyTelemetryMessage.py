from json import dumps, loads
from typing import Self, Literal
from decimal import Decimal

from communications.kafka import Message

class SupplyTelemetryMessage(Message):
    def __init__(
        self, 
        msg_type: Literal["ticket", "supplying"],
        supply_id: int, 
        price: Decimal, 
        consumption: int
        ) -> None:
        super().__init__()
        self.type = msg_type
        self.supply_id = supply_id
        self.price = price
        self.consumption = consumption
        
    def to_payload(self) -> str:
        return dumps({
            "type": self.type,
            "supply_id": self.supply_id,
            "price": str(self.price), 
            "consumption": self.consumption
        })
        
    @classmethod
    def from_payload(cls, payload: str) -> Self:
        json_dict = loads(payload)
        msg_type = json_dict['type']
        supply_id = json_dict['supply_id']
        price = Decimal(json_dict['price']) 
        consumption = json_dict['consumption']
        
        return cls(msg_type, supply_id, price, consumption)

    def is_ticket(self) -> bool:
        return self.type == 'ticket'