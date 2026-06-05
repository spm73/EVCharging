from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal


@dataclass
class SupplyData:
    supply_id: int
    start_time: datetime          = field(default_factory=datetime.now)
    kwh_accumulated: int          = 0
    amount_accumulated: Decimal   = Decimal() # price

    def to_dict(self) -> dict:
        return {
            'supply_id':          self.supply_id,
            'start_time':         self.start_time.isoformat(),
            'kwh_accumulated':    self.kwh_accumulated,
            'amount_accumulated': str(self.amount_accumulated),
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'SupplyData':
        return cls(
            supply_id          = data['supply_id'],
            start_time         = datetime.fromisoformat(data['start_time']),
            kwh_accumulated    = data['kwh_accumulated'],
            amount_accumulated = Decimal(data['amount_accumulated']),
        )
