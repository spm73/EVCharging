from abc import ABC, abstractmethod
from typing import Self

class Message(ABC):
    @abstractmethod
    def to_payload(self) -> str:
        pass
    
    @staticmethod
    @abstractmethod
    def from_payload(payload: str) -> Self:
        pass