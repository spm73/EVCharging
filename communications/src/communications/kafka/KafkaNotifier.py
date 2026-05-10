from typing import Callable, TypeVar, Generic

from .Message import Message

M = TypeVar('M', bound=Message)

class KafkaNotifier(Generic[M]):
    def __init__(self):
        self.__subscribers: list[Callable[[M], None]] = []

    def add_subscriber(self, subscriber: Callable[[M], None]) -> None:
        self.__subscribers.append(subscriber)

    def remove_subscriber(self, subscriber: Callable[[M], None]) -> None:
        self.__subscribers.remove(subscriber)

    def notify(self, message: M) -> None:
        for subscriber_action in self.__subscribers:
            subscriber_action(message)
