from json import loads
from typing import Any

from confluent_kafka import Consumer

class SupplyReqConsumer:
    SUBSCRIBED_TOPIC = ['supply-req']
    def __init__(self, kafka_ip: str, kafka_port: int):
        conf = {
            'bootstrap.servers': f'{kafka_ip}:{kafka_port}',
            'group.id': 'central',
            # following configs can be ommited
            'auto.offset.reset': 'earliest', # process everything not committed
            'enable.auto.commit': False, # manual commit management
        }
        self.consumer = Consumer(conf)
        self.consumer.subscribe(SupplyReqConsumer.SUBSCRIBED_TOPIC)
        
    def close(self):
        self.consumer.close()
        
    def get_request(self) -> dict[str: Any] | None:
        try:
            raw_msg = self.consumer.poll(timeout=1.0)
            if not raw_msg:
                return None
            
            if raw_msg.error():
                pass
            
            msg = dict(loads(raw_msg.value().decode('utf-8')))
            self.consumer.commit(raw_msg)
            return msg
        except RuntimeError:
            print("Consumer is closed and cannot make operations")