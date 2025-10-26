# from random import choice

class SupplyData:
    CONSUMPTION_INCREASE = 22
    def __init__(self, price):
        self.consumption = 0
        self.cost = 0
        self.price = price
        
    def get_consumption(self) -> float:
        return self.consumption
    
    def get_cost(self) -> float:
        return self.cost
    
    def get_price(self) -> float:
        return self.price
    
    def _update_consumption(self):
        self.consumption += SupplyData.CONSUMPTION_INCREASE
    
    def _update_cost(self):
        self.cost += SupplyData.CONSUMPTION_INCREASE * self.price

    def update_supply(self):
        self._update_consumption()
        self._update_cost()
        
    # CONSUMPTIONS = [
    #     3.7, 3.8, 4.0, 4.2, 5.5, 6.6, 7.0, 7.2, 
    #     7.4, 8.0, 11.0, 11.2, 16.5, 17.0, 22.0, 22.5, 
    #     50.0, 75.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0
    # ]
    # PRICES = [
    #     0.105, 0.108, 0.110, 0.115, 0.120, 0.125, 0.130, 0.145, 
    #     0.160, 0.175, 0.190, 0.205, 0.220, 0.215, 0.200, 0.185, 
    #     0.170, 0.155, 0.140, 0.135, 0.130, 0.125, 0.120, 0.115
    # ]
    
    # def __init__(self):
    #     self.current_consumption = 0
    #     self.current_price = 0
    #     self.accumulated_consumption = 0
    #     self.accumulated_price = 0
        
    # def get_current_consumption(self) -> float:
    #     return self.current_consumption
    
    # def get_current_price(self) -> float:
    #     return self.current_price
    
    # def get_accumulated_consumption(self) -> float:
    #     return self.accumulated_consumption
    
    # def get_accumulated_price(self) -> float:
    #     return self.accumulated_price
    
    # def update_consumption(self):
    #     self.accumulated_consumption += self.accumulated_consumption
    #     self.current_consumption = choice(SupplyData.CONSUMPTIONS)
    
    # def update_price(self):
    #     self.accumulated_price += self.current_price * self.current_consumption
    #     self.current_price = choice(SupplyData.PRICES)