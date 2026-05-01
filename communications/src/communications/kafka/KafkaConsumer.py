from confluent_kafka import Consumer, KafkaError
from typing import Callable, Type
from threading import Thread, Event

from .Message import Message
from .KafkaBrokerInfo import KafkaBrokerInfo
from .KafkaNotifier import KafkaNotifier

class KafkaConsumer():
    def __init__(
        self,
        broker_info: KafkaBrokerInfo, 
        topic: str, 
        group_id: str,
        message_class: Type[Message],
        filter_func: Callable[[Message], bool] | None
    ) -> None:
        conf = {
            'bootstrap.servers': broker_info.get_broker_endpoint(),
            'group.id': group_id
        }
        self.__topic = topic
        self.__message_class = message_class
        self.__consumer = Consumer(conf)
        self.__consumer.subscribe([topic])
        self.__filter_func = filter_func
        self.__notifier = KafkaNotifier()
        self.__is_polling = Event()
        self.__thread = Thread(target=self.__polling_loop, daemon=True)
        self.__thread.start()
        
    def stop_polling(self):
        self.__is_polling.clear()
        self.__thread.join()
        self.__consumer.close()
        
    def get_notifier(self) -> KafkaNotifier:
        return self.__notifier
    
    def __should_notify(self, message: Message) -> bool:
        if self.__filter_func is not None:
            return self.__filter_func(message)
        
        return True
        
    def start_polling(self) -> None:
        self.__is_polling.set()
    
    def __polling_loop(self):
        self.__is_polling.wait()
        while self.__is_polling.is_set():
            msg = self.__consumer.poll(1.0)
            if msg is None:
                continue
            if msg.error():
                if msg.error().code() != KafkaError._PARTITION_EOF:
                    print(f"{self.__class__}:{self.__topic} Error: {msg.error()}")
                continue

            message = self.__message_class.from_payload(msg.value().decode('utf-8'))
            if self.__should_notify(message):
                self.__notifier.notify(message)
        
        