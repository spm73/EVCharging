from json import loads
from typing import Any

from confluent_kafka import Consumer

class DirectivesConsumer:
    SUBSCRIBED_TOPIC = ['central-directives']
    def __init__(self, kafka_ip: str, kafka_port: int, cp_id: str):
        conf = {
            'bootstrap.servers': f'{kafka_ip}:{kafka_port}',
            'group.id': cp_id,
            'auto.offset.reset': 'latest',
            'enable.auto.commit': True
        }
        self.consumer = Consumer(conf)
        self.consumer.subscribe(DirectivesConsumer.SUBSCRIBED_TOPIC)
        self.cp_id = cp_id
        
    def close(self):
        self.consumer.close()
        
    def get_directive(self) -> dict[str: Any] | None:
        try: 
            raw_msg = self.consumer.poll(timeout=1.0)
            if not raw_msg:
                return None
            
            if raw_msg.error():
                pass
            
            msg = dict(loads(raw_msg.value().decode('utf-8')))
            target = msg['target']
            if target == 'all' or msg == self.cp_id:
                return msg
            return None
        except RuntimeError:
            print("Consumer is closed and cannot make operations")
            