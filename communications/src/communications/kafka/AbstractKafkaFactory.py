from abc import ABC, abstractmethod
from typing import Type

from .KafkaBrokerInfo import KafkaBrokerInfo
from .KafkaProducer import KafkaProducer
from .KafkaConsumer import KafkaConsumer
from .Message import Message

class AbstractKafkaFactory(ABC):
    def __init__(self, broker_info: KafkaBrokerInfo) -> None:
        self._broker_info = broker_info
        
    def create_producer(self, topic: str) -> KafkaProducer:
        return KafkaProducer(self._broker_info, topic)
    
    @abstractmethod
    def create_consumer(
        self, 
        topic: str, 
        group_id: str, 
        message_class: Type[Message]
        ) -> KafkaConsumer:
        pass