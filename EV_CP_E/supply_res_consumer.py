from json import loads
from typing import Any

from confluent_kafka import Consumer

class SupplyResConsumer:
    SUBSCRIBED_TOPIC = ['supply-res']
    def __init__(self, kafka_ip: str, kafka_port: int, cp_id: str):
        conf = {
            'bootstrap.servers': f'{kafka_ip}:{kafka_port}',
            'group.id': cp_id,
            # following configs can be ommited
            'auto.offset.reset': 'latest',
            'enable.auto.commit': True,
        }
        self.consumer = Consumer(conf)
        self.consumer.subscribe(SupplyResConsumer.SUBSCRIBED_TOPIC)
        self.cp_id = cp_id
        
    def close(self):
        self.consumer.close()
        
    def get_response(self) -> dict[str: Any] | None:
        try:
            raw_msg = self.consumer.poll(timeout=1.0)
            if not raw_msg:
                return None
            
            if raw_msg.error():
                pass
            
            msg = loads(raw_msg.value().decode('utf-8'))
            if msg['applicant_id'] != self.cp_id:
                return None
            return msg
        except RuntimeError:
            print("Consumer is closed and cannot make operations")