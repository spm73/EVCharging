import socket

class SocketConnection:
    ENQ = chr(5).encode()
    EOT = chr(4).encode()
    STX = chr(2).encode()
    ETX = chr(3).encode()
    ACK = chr(6).encode()
    NACK = chr(21).encode()
    ATTEMPTS = 3
    
    def __init__(self, socket: socket.socket) -> None:
        self.__socket = socket
        socket.settimeout(1)
        
    def close(self) -> None:
        try:
            self.__socket.send(SocketConnection.EOT)
        except (ConnectionError, OSError):
            pass
        self.__socket.close()
        
    def send_handshake(self) -> bool:
        answer = None
        attempts = 0
        while not answer and attempts < SocketConnection.ATTEMPTS:
            try:
                self.__socket.send(SocketConnection.ENQ)
            except ConnectionError:
                break
            try:
                answer = self.__socket.recv(1)
                if answer == SocketConnection.ACK:
                    return True
                
                answer = None
                attempts += 1
            except TimeoutError:
                attempts += 1
                continue
            except ConnectionResetError:
                break
        
        print("Closing connection: Could not complete handshake")
        self.close()
        return False
        
    def receive_handshake(self) -> bool:
        message = None
        attempts = 0
        while not message and attempts < SocketConnection.ATTEMPTS:
            try:
                message = self.__socket.recv(1)
                if message == SocketConnection.ENQ:
                    try:
                        self.__socket.send(SocketConnection.ACK)
                        return True
                    except ConnectionError:
                        break
                
                self.__socket.send(SocketConnection.NACK)
                message = None
                attempts += 1
            except TimeoutError:
                attempts += 1
                continue
            except ConnectionResetError:
                break
    
        print("Closing connection: Could not complete handshake")
        self.close()
        return False
    
    def __calculate_lrc(self, data: bytes) -> bytes:
        lrc = 0
        for byte in data:
            lrc ^= byte
        return bytes([lrc])
    
    def __build_frame(self, message: str) -> bytes:
        content = message.encode()
        lrc = self.__calculate_lrc(content)
        return SocketConnection.STX + content + SocketConnection.ETX + lrc
    
    def __receive_frame(self) -> str | None:
        attempts = 0
        while attempts < SocketConnection.ATTEMPTS:
            try:
                # Esperar STX
                byte = self.__socket.recv(1)
                if byte != SocketConnection.STX:
                    attempts += 1
                    continue
            except TimeoutError:
                attempts += 1
                continue
            except ConnectionResetError:
                self.close()
                return None
            
            try:
                # Leer hasta ETX
                content = b''
                byte = None
                while byte != SocketConnection.ETX:
                    byte = self.__socket.recv(1)
                    if byte == b'':
                        raise ConnectionResetError()
                    if byte != SocketConnection.ETX:
                        content += byte

                # Leer LRC
                received_lrc = self.__socket.recv(1)
                expected_lrc = self.__calculate_lrc(content)

                if received_lrc != expected_lrc:
                    self.__socket.send(SocketConnection.NACK)
                    attempts += 1
                    continue

                self.__socket.send(SocketConnection.ACK)
                return content.decode()
            except TimeoutError:
                return None
            except ConnectionResetError:
                self.close()
                return None

        return None

    def send(self, message: str) -> bool:
        frame = self.__build_frame(message)
        attempts = 0
        while attempts < SocketConnection.ATTEMPTS:
            try:
                self.__socket.send(frame)
                ack = self.__socket.recv(1)
                if ack == SocketConnection.ACK:
                    return True
                attempts += 1
            except TimeoutError:
                attempts += 1
            except ConnectionError:
                self.close()
                return False

        return False

    def receive(self) -> str | None:
        message = self.__receive_frame()
        if message is not None:
            return message
            
        print("Closing connection: Could not receive message")
        self.close()
        return None