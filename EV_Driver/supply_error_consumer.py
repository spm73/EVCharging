from json import loads
from typing import Any

from confluent_kafka import Consumer, KafkaError, KafkaException

class SupplyErrorConsumer:
    SUBSCRIBED_TOPIC = ['supply-error']
    def __init__(self, kafka_ip: str, kafka_port: int, driver_id: str, supply_id: int):
        conf = {
            'bootstrap.servers': f'{kafka_ip}:{kafka_port}',
            'group.id': driver_id,
            # following configs can be ommited
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': True,
        }
        self.consumer = Consumer(conf)
        self.consumer.subscribe(SupplyErrorConsumer.SUBSCRIBED_TOPIC)
        self.supply_id = supply_id
        
    def close(self):
        self.consumer.close()
        
    def get_error(self) -> dict[str, Any] | None:
        try:
            raw_msg = self.consumer.poll(timeout=2.0)
            if not raw_msg:
                return None
            
            if raw_msg.error():
                error_code = raw_msg.error().code()
                if error_code != KafkaError._PARTITION_EOF:
                    raise KafkaException(raw_msg.error())
            
            msg = loads(raw_msg.value().decode('utf-8'))
            if msg['supply_id'] != self.supply_id:
                return None
            return msg
        except RuntimeError:
            print("Consumer is closed and cannot make operations")