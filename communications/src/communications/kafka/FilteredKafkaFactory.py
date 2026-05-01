from typing import Callable

from .AbstractKafkaFactory import AbstractKafkaFactory
from .Message import Message
from .KafkaBrokerInfo import KafkaBrokerInfo
from .KafkaConsumer import KafkaConsumer

class FilteredKafkaFactory(AbstractKafkaFactory):
    def __init__(self, broker_info: KafkaBrokerInfo, filter_func: Callable[[Message], bool]):
        super().__init__(broker_info)
        self.__filter_func = filter_func
        
    def create_consumer(self, topic: str, group_id: str) -> KafkaConsumer:
        return KafkaConsumer(self._broker_info, topic, group_id, self.__filter_func)