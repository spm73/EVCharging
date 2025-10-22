import socket

from closing_connection_exception import ClosingConnectionException
from connection_closed_exception import ConnectionClosedException

class STXETXConnection:
    ENQ_MESSAGE = chr(5).encode()
    EOT_MESSAGE = chr(4).encode()
    STX_HEADER = chr(2).encode()
    ETX_HEADER = chr(3).encode()
    ACK_HEADER = chr(6).encode()
    NACK_HEADER = chr(21).encode()
    # ENQ_MESSAGE = '<ENQ>'.encode()
    # EOT_MESSAGE = '<EOT>'.encode()
    # STX_HEADER = '<STX>'.encode()
    # ETX_HEADER = '<ETX>'.encode()
    # ACK_HEADER = '<ACK>'.encode()
    # NACK_HEADER = '<NACK>'.encode()
    def __init__(self, ip_addr: str, port_number: int):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect((ip_addr, port_number))
        
    def __init__(self, client_socket: socket.socket):
        self.client = client_socket
        
    def enq_message(self):
        self.client.sendall(STXETXConnection.ENQ_MESSAGE)
        answer = self.client.recv(6).decode()
        if not answer:
            raise ConnectionClosedException('No response from server')
        
    def enq_answer(self):
        answer = self.client.recv(6).decode()
        if not answer:
            raise ConnectionClosedException('No response from server')
        self.send_ack()
        
    def close(self):
        self.client.close()
            
    def eot_message(self):
        self.client.sendall(STXETXConnection.EOT_MESSAGE)
        self.close()
        
    def send_ack(self):
        self.client.sendall(STXETXConnection.ACK_HEADER)
    
    def send_nack(self):
        self.client.sendall(STXETXConnection.NACK_HEADER)
        
    def send_message(self, message: str):
        crc_message = bytes(ord(char) ^ ord(char) for char in message)
        msg = STXETXConnection.STX_HEADER + message.encode() + STXETXConnection.ETX_HEADER + crc_message
        confirmation = None
        while confirmation is None or confirmation == STXETXConnection.NACK_HEADER:
            self.client.sendall(msg)
            confirmation = self.client.recv(6).decode()
            if not confirmation:
                raise ConnectionClosedException('No response from server')
        
    def recv_message(self) -> str:
        answer = None
        lrc = None
        comprobation = None
        while answer is None or comprobation != lrc:
            raw_answer = self.client.recv(1024)
            if not raw_answer:
                raise ConnectionClosedException('No response from server')
            elif raw_answer == STXETXConnection.EOT_MESSAGE:
                raise ClosingConnectionException()
            
            stx_answer, lrc = raw_answer.split(STXETXConnection.ETX_HEADER)
            answer = stx_answer.removeprefix(STXETXConnection.STX_HEADER)
            comprobation = bytes(ord(byte) ^ ord(byte) for byte in answer)
            if comprobation == lrc:
                self.send_ack()
            else:
                self.send_nack()
        
        return answer.decode()