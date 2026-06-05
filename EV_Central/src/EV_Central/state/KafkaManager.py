from threading import Lock
from communications.kafka import KafkaFactory, KafkaBrokerInfo

class KafkaManager:
    _instance = None
    _instance_lock = Lock()
    
    def __new__(cls, *args, **kwargs):
        with cls._instance_lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self, broker_info: KafkaBrokerInfo) -> None:
        if hasattr(self, '_initialized'):
            return
        self.__factory = KafkaFactory(broker_info)
        self._initialized = True
    
    def get_factory(self) -> KafkaFactory:
        return self.__factory
    