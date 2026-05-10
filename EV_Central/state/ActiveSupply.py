from decimal import Decimal

class ActiveSupply:
    def __init__(self, supply_id: int):
        self.id = supply_id
        self.consumption = 0
        self.price = Decimal(0)
        
    def update_data(self, consumption: int, price: Decimal) -> None:
        self.consumption = consumption
        self.price = price