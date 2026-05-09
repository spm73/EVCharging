from abc import ABC, abstractmethod
from typing import Self

class Message(ABC):
    @abstractmethod
    def to_payload(self) -> str:
        pass
    
    @classmethod
    @abstractmethod
    def from_payload(cls, payload: str) -> Self:
        pass