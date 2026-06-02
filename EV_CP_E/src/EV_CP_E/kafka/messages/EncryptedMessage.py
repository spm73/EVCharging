from communications.kafka import Message
from typing import Self, Type
from cryptography.fernet import Fernet
from json import dumps, loads

from .SupplyTelemetryMessage import SupplyTelemetryMessage
from .CentralCommandMessage import CentralCommandMessage
from .StartSupplyMessage import StartSupplyMessage

class EncryptedMessage(Message):
    _CLASS_TRANSLATOR: dict[str, Type[Message]] = {
        'SupplyTelemetryMessage': SupplyTelemetryMessage,
        'CentralCommandMessage': CentralCommandMessage,
        'StartSupplyMessage': StartSupplyMessage,
    }
    
    # En el Engine, la clave simétrica se actualizará de forma estática 
    # cuando el Monitor reciba el mensaje KEY#...
    _cipher_key: bytes | None = None

    @classmethod
    def set_cipher_key(cls, key: bytes | None) -> None:
        cls._cipher_key = key
    
    def __init__(self, cp_id: str, message: Message) -> None:
        super().__init__()
        self.cp_id = cp_id
        self.message = message
    
    def to_payload(self) -> str:
        key = self._cipher_key
        if not key:
            raise RuntimeError(f"Engine has no cipher key assigned")
        fernet = Fernet(key)
        payload_to_encrypt = dumps({
            'type': self.message.__class__.__name__,
            'content': self.message.to_payload()
        }).encode()
        encrypted_payload = fernet.encrypt(payload_to_encrypt).decode()
        return dumps({
            'cp_id': self.cp_id,
            'payload': encrypted_payload
        })    
    
    @classmethod
    def from_payload(cls, payload: str) -> Self:
        json_dict = loads(payload)
        cp_id = json_dict['cp_id']
        msg_payload = json_dict['payload'].encode()
        
        key = cls._cipher_key
        if not key:
            raise RuntimeError(f"Engine has no cipher key assigned to decrypt")
        fernet = Fernet(key)
        decrypted_payload = loads(fernet.decrypt(msg_payload).decode())
        message_type = decrypted_payload.get('type')
        if message_type is None:
            raise RuntimeError(f"No attribute type in payload")
        message_class = cls._CLASS_TRANSLATOR.get(message_type)
        if message_class is None:
            raise RuntimeError(f"Unknown message type: {message_type}")
        message = message_class.from_payload(decrypted_payload['content'])
        return cls(cp_id, message)
