from json import loads
from typing import Any

from confluent_kafka import Consumer, KafkaError

class SupplyResConsumer:
    SUBSCRIBED_TOPIC = ['supply-res']
    def __init__(self, kafka_ip: str, kafka_port: int, driver_id: str):
        conf = {
            'bootstrap.servers': f'{kafka_ip}:{kafka_port}',
            'group.id': driver_id,
            # following configs can be ommited
            'auto.offset.reset': 'latest',
            'enable.auto.commit': True,
        }
        self.consumer = Consumer(conf)
        self.consumer.subscribe(SupplyResConsumer.SUBSCRIBED_TOPIC)
        self.driver_id = driver_id
        
    def close(self):
        self.consumer.close()
        
    def get_response(self) -> dict[str: Any] | None:
        try:
            raw_msg = self.consumer.poll(timeout=1.0)
            if not raw_msg:
                return None
            
            if raw_msg.error():
                error_code = raw_msg.error().code()
                if error_code != KafkaError._PARTITION_EOF:
                    raise KafkaError(raw_msg.error())
            
            msg = loads(raw_msg.value().decode('utf-8'))
            if msg['applicant_id'] != self.driver_id:
                return None
            return msg
        except RuntimeError:
            print("Consumer is closed and cannot make operations")