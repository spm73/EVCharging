from decimal import Decimal

class ActiveSupply:
    def __init__(self, supply_id: int, driver_id: str | None):
        self.id = supply_id
        self.driver_id = driver_id
        self.consumption = 0
        self.price = Decimal(0)
        
    def update_data(self, consumption: int, price: Decimal) -> None:
        self.consumption = consumption
        self.price = price