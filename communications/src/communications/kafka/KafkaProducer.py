from confluent_kafka import Producer

from .KafkaBrokerInfo import KafkaBrokerInfo
from .Message import Message

class KafkaProducer:
    def __init__(self, broker: KafkaBrokerInfo, topic: str) -> None:
        conf = {
            'bootstrap.servers': broker.get_broker_endpoint()
        }
        self.__producer = Producer(conf)
        self.__topic = topic
        
    def get_topic(self) -> str:
        return self.__topic
    
    def send_message(self, message: Message, key: str) -> None:
        self.__producer.produce(
            self.__topic,
            value=message.to_payload(),
            key=key
        )
        self.__producer.flush()