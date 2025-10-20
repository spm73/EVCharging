from json import loads
from typing import Any

from confluent_kafka import Consumer

class SupplyInfoConsumer:
    SUBSCRIBED_TOPIC = ['supply-data']
    def __init__(self, kafka_ip: str, kafka_port: int):
        conf = {
            'bootstrap.servers': f'{kafka_ip}:{kafka_port}',
            'group.id': 'central',
            'auto.offset.reset': 'latest', # process everything not committed
            'enable.auto.commit': True, # manual commit management
        }
        self.consumer = Consumer(conf)
        self.consumer.subscribe(SupplyInfoConsumer.SUBSCRIBED_TOPIC)
        
    def close(self):
        self.consumer.close()
        
    def get_request(self, supply_id: int) -> dict[str: Any] | None:
        try:
            raw_msg = self.consumer.poll(timeout=1.0)
            if not raw_msg:
                return None
            
            if raw_msg.error():
                pass
            
            msg = loads(raw_msg.value().decode('utf-8'))
            if msg['supply_id'] != supply_id:
                return None
            return msg
        except RuntimeError:
            print("Consumer is closed and cannot make operations")