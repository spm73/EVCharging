from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from EV_CP_E.CPEngine import CPEngine
    from EV_CP_E.Event import Event


class State(ABC):

    @abstractmethod
    def handle(self, event: 'Event', context: 'CPEngine') -> None:
        """Procesa un evento y ejecuta las transiciones oportunas."""
        pass

    def on_enter(self, context: 'CPEngine') -> None:
        """Se ejecuta justo después de entrar en este estado."""
        pass

    def on_exit(self, context: 'CPEngine') -> None:
        """Se ejecuta justo antes de salir de este estado."""
        pass

    def __str__(self) -> str:
        return self.__class__.__name__
