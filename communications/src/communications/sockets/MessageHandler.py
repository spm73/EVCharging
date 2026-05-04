from typing import Callable

class MessageHandler:
    def __init__(self, default: Callable[[str], str] | None =None):
        self.__handlers: dict[str, Callable[[str], str]] = {}
        self.__default = default

    def register(self, message_type, callback) -> None:
        self.__handlers[message_type] = callback
        
    def delete(self, message_type) -> None:
        self.__handlers.pop(message_type, None)

    def handle(self, message) -> str | None:
        message_type = message.split('#')[0]
        handler = self.__handlers.get(message_type, self.__default)
        if handler is None:
            return None
        return handler(message)