from supply_data import SupplyData
from supply_info_producer import SupplyInfoProducer

class SupplyInfo:
    def __init__(self, kafka_ip: str, kafka_port: int, supply_id: int, price: float):
        self.producer = SupplyInfoProducer(kafka_ip, kafka_port, supply_id)
        self.data = SupplyData(price)
    
    def send_info(self):
        self.producer.send_supplying_msg(
            self.data.get_consumption(),
            self.data.get_cost()
        )
        self.data.update_supply()
        
    def send_ticket(self):
        self.producer.send_ticket(
            self.data.get_consumption(),
            self.data.get_cost()
        )
        
    def get_consumption(self) -> float:
        return self.data.get_consumption()
    
    def get_cost(self) -> float:
        return self.data.get_cost()
    
    # def __init__(self, kafka_ip: str, kafka_port: int, supply_id: int):
    #     self.producer = SupplyInfoProducer(kafka_ip, kafka_port, supply_id)
    #     self.data = SupplyData()
        
    # def send_info(self):
    #     self.producer.send_supplying_msg(
    #         self.data.get_current_consumption(),
    #         self.data.get_current_price()
    #     )
    #     self.data.update_consumption()
    #     self.data.update_price()
        
    # def send_ticket(self):
    #     self.producer.send_ticket(
    #         self.data.accumulated_consumption,
    #         self.data.accumulated_price
    #     )
        
    # def get_current_consumption(self) -> float:
    #     return self.data.get_current_consumption()
    
    # def get_current_price(self) -> float:
    #     return self.data.get_current_price()
    
    # def get_accumulated_consumption(self) -> float:
    #     return self.data.get_accumulated_consumption()
    
    # def get_accumulated_price(self) -> float:
    #     return self.data.get_accumulated_price()