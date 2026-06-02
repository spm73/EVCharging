from typing import TYPE_CHECKING

from ..State import State

if TYPE_CHECKING:
    from ..CPEngine import CPEngine
    from ..Event import Event


class WaitingForKeyState(State):
    """
    Estado inicial y de recuperación.
    El Engine no puede hacer nada hasta que el Monitor se conecte y envíe la clave.
    """

    def on_enter(self, context: 'CPEngine') -> None:
        context.clear_cipher_key()

    def handle(self, event: 'Event', context: 'CPEngine') -> None:
        pass  # T7 lo implementará
