import socket
import ssl
import threading
from .SocketConnection import SocketConnection
from typing import Callable

class SocketServer:
    def __init__(self, ip: str, port: int, handler: Callable[[SocketConnection], None], ssl_context: ssl.SSLContext | None = None):
        self.__ip = ip
        self.__port = port
        self.__handler = handler
        self.__ssl_context = ssl_context
        self.__server_socket: socket.socket | None = None
        self.__running = False

    def start(self) -> None:
        self.__server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__server_socket.bind((self.__ip, self.__port))
        self.__server_socket.listen()
        self.__running = True

        thread = threading.Thread(target=self.__accept_loop, daemon=True)
        thread.start()

    def __accept_loop(self) -> None:
        while self.__running:
            try:
                client_sock, address = self.__server_socket.accept()
                if self.__ssl_context:
                    client_sock = self.__ssl_context.wrap_socket(client_sock, server_side=True)
                connection = SocketConnection(client_sock)
                thread = threading.Thread(target=self.__handle_client, args=(connection,), daemon=True)
                thread.start()
            except OSError:
                break

    def __handle_client(self, connection: SocketConnection) -> None:
        try:
            self.__handler(connection)
        finally:
            connection.close()

    def stop(self) -> None:
        self.__running = False
        if self.__server_socket:
            self.__server_socket.close()
            self.__server_socket = None