from typing import Callable

class MessageHandler:
    def __init__(self, default: Callable[[str], str] | None =None):
        self.__handlers: dict[str, Callable[[str], str]] = {}
        self.__default = default

    def register(self, message_type: str, callback: Callable[[str], str]) -> None:
        self.__handlers[message_type] = callback
        
    def delete(self, message_type: str) -> None:
        self.__handlers.pop(message_type, None)

    def handle(self, message: str, split_by: str = '#') -> str | None:
        message_type = message.split(split_by)[0]
        handler = self.__handlers.get(message_type, self.__default)
        if handler is None:
            return None
        return handler(message)