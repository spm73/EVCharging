from json import dumps

from confluent_kafka import Producer

class SupplyInfoProducer:
    TOPIC_NAME = 'supply-data'
    def __init__(self, kafka_ip: str, kafka_port: int):
        conf = {
            'bootrsap.servers': f'{kafka_ip}:{kafka_port}'
        }
        self.producer = Producer(conf)
        
    def send_supplying_msg(self, consumption: float, price: float, supply_id: int):
        msg = {
            'supply_id': supply_id,
            'type': 'supplying',
            'consumption': consumption,
            'price': price
        }
        
        json_msg = dumps(msg)
        self.producer.produce(SupplyInfoProducer.TOPIC_NAME, value=json_msg)
    
    def send_ticket(self, total_consumption: float, total_price: float, supply_id: int):
        msg = {
            'supply_id': supply_id,
            'type': 'ticket',
            'consumption': total_consumption,
            'price': total_price
        }
        
        json_msg = dumps(msg)
        self.producer.produce(SupplyInfoProducer.TOPIC_NAME, value=json_msg)