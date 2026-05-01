from .AbstractKafkaFactory import AbstractKafkaFactory
from .KafkaBrokerInfo import KafkaBrokerInfo
from .KafkaConsumer import KafkaConsumer

class SimpleKafkaFactory(AbstractKafkaFactory):
    def __init__(self, broker_info: KafkaBrokerInfo):
        super().__init__(broker_info)
        
    def create_consumer(self, topic: str, group_id: str) -> KafkaConsumer:
        return KafkaConsumer(self._broker_info, topic, group_id, None)