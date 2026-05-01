from typing import Callable

from .Message import Message

class KafkaNotifier:
    def __init__(self):
        self.__subscribers: list[Callable[[Message], None]] = []

    def add_subscriber(self, subscriber: Callable[[Message], None]) -> None:
        self.__subscribers.append(subscriber)

    def remove_subscriber(self, subscriber: Callable[[Message], None]) -> None:
        self.__subscribers.remove(subscriber)

    def notify(self, message: Message) -> None:
        for subscriber_action in self.__subscribers:
            subscriber_action(message)
