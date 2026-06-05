from communications.sockets import SocketClient
from decimal import Decimal

class EngineStatus:
    STOPPED       = "Stopped"
    ACTIVE        = "Active"
    SUPPLYING     = "Supplying"
    BROKEN_DOWN   = "Broken Down"
    DISCONNECTED  = "Disconnected"


class EngineClient:
    def __init__(self, host: str, port: int) -> None:
        self.__client = SocketClient(host, port)

    # ── Conexión ────────────────────────────────────────────────────────────

    def connect(self) -> bool:
        return self.__client.connect()

    def disconnect(self) -> None:
        self.__client.send("BYE#")
        self.__client.disconnect()

    # ── Protocolo ───────────────────────────────────────────────────────────

    def get_status(self) -> str | None:
        """
        Sends STATUS# and parses the response.
        Returns (status_str, SupplyData | None) or None if connection failed.
        """
        response = self.__client.send("STATUS#")
        if response is None:
            return None

        parts = response.split('#')
        # Expected: STATUS#<status>
        if parts[0] != "STATUS" or len(parts) < 2:
            return None

        status = parts[1]

        return status

    def send_config(self, cp_id: str, cp_key: str, price: Decimal) -> bool:
        """Sends the CP ID, symmetric encryption key, and CP price to the Engine."""
        response = self.__client.send(f"CONFIG#{cp_id}#{cp_key}#{str(price)}")
        return response is not None and response.startswith("CONFIG#copy")

    def send_out_of_service(self) -> bool:
        """Orders the engine to go out of service after current supply ends."""
        response = self.__client.send("OUT_OF_SERVICE#")
        return response is not None and response.startswith("OUT_OF_SERVICE#copy")