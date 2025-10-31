from json import dumps
from typing import Any

from confluent_kafka import Producer

class SupplyInfoProducer:
    TOPIC_NAME = 'supply-data2'
    def __init__(self, kafka_ip: str, kafka_port: int):
        conf = {
            'bootstrap.servers': f'{kafka_ip}:{kafka_port}'
        }
        self.producer = Producer(conf)
        
    def repeat_msg(self, msg: dict[str, Any]):
        json_msg = dumps(msg)
        self.producer.produce(SupplyInfoProducer.TOPIC_NAME, value=json_msg)
        self.producer.flush()

    def send_supplying_msg(self, consumption: float, price: float):
        msg = {
            'supply_id': self.supply_id,
            'type': 'supplying',
            'consumption': consumption,
            'price': price
        }
        
        json_msg = dumps(msg)
        self.producer.produce(SupplyInfoProducer.TOPIC_NAME, value=json_msg)
        self.producer.flush()
    
    def send_ticket(self, total_consumption: float, total_price: float):
        msg = {
            'supply_id': self.supply_id,
            'type': 'ticket',
            'consumption': total_consumption,
            'price': total_price
        }
        
        json_msg = dumps(msg)
        self.producer.produce(SupplyInfoProducer.TOPIC_NAME, value=json_msg)
        self.producer.flush()