from communications.sockets import SocketClient

class CentralClient:
    def __init__(self, host: str, port: int) -> None:
        self.__client = SocketClient(host, port)
        self.__cp_key: str | None = None

    # ── Conexión ────────────────────────────────────────────────────────────

    def connect(self) -> bool:
        return self.__client.connect()

    def disconnect(self) -> None:
        self.__client.send("BYE#")
        self.__client.disconnect()

    # ── Protocolo ───────────────────────────────────────────────────────────

    def authenticate(self, cp_id: str, jwt_token: str) -> str | None:
        """
        Sends AUTH#<cp_id>#<jwt_token>.
        Returns the symmetric cp_key on success, None on failure.
        """
        response = self.__client.send(f"AUTH#{cp_id}#{jwt_token}")
        if response is None:
            return None

        parts = response.split('#')
        # Expected: AUTH#accepted#<cp_key> or AUTH#denied
        if parts[0] != "AUTH" or len(parts) < 2:
            return None

        if parts[1] == "accepted" and len(parts) == 3:
            self.__cp_key = parts[2]
            return self.__cp_key

        return None

    def send_status(self, status: str) -> bool:
        """
        Sends STATUS#<status> to Central.
        Returns True if Central replied with STATUS#copy.
        """
        response = self.__client.send(f"STATUS#{status}")
        return response is not None and response.startswith("STATUS#copy")

    def get_cp_key(self) -> str | None:
        return self.__cp_key