from typing import Type, Callable

from .KafkaBrokerInfo import KafkaBrokerInfo
from .KafkaProducer import KafkaProducer
from .KafkaConsumer import KafkaConsumer, M

class KafkaFactory:
    def __init__(self, broker_info: KafkaBrokerInfo) -> None:
        self._broker_info = broker_info
        
    def create_producer(self, topic: str) -> KafkaProducer:
        return KafkaProducer(self._broker_info, topic)
    
    def create_consumer(
        self, 
        topic: str, 
        group_id: str, 
        message_class: Type[M],
        filter_func: Callable[[M], bool] | None = None,
        auto_offset_reset: str = 'latest'
        ) -> KafkaConsumer[M]:
        return KafkaConsumer(self._broker_info, topic, group_id, message_class, filter_func, auto_offset_reset)