import socket
import ssl
from .SocketConnection import SocketConnection
from typing import Callable, Self

class SocketClient:
    def __init__(self, host: str, port: int, on_connect: Callable[[Self], str]=None, ssl_context: ssl.SSLContext | None = None):
        self.__host = host
        self.__port = port
        self.__ssl_context = ssl_context
        self.__on_connect = on_connect
        self.__connection: SocketConnection | None = None

    def connect(self) -> bool:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            if self.__ssl_context:
                sock = self.__ssl_context.wrap_socket(sock, server_hostname=self.__host)
            sock.connect((self.__host, self.__port))
            self.__connection = SocketConnection(sock)
            if self.__on_connect:
                if not self.__on_connect(self):
                    self.__connection.close()
                    self.__connection = None
                    return False
            return True
        except OSError:
            return False

    def disconnect(self) -> None:
        if self.__connection:
            self.__connection.close()
            self.__connection = None

    def send(self, message: str) -> str | None:
        if not self.__connection:
            return None

        if self.__connection.send(message):
            return self.__connection.receive()

        # Reconexión automática
        if self.connect():
            if self.__connection.send(message):
                return self.__connection.receive()

        return None