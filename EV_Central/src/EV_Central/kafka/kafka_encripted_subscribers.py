from EV_Central.kafka.kafka_subscribers import cp_request_handler, resend_telemetry
from EV_Central.kafka.messages import EncryptedMessage

def cp_encrypted_request_handler(message: EncryptedMessage) -> None:
    cp_request_handler(message.message)
    

def resend_encrypted_telemetry(message: EncryptedMessage) -> None:
    resend_telemetry(message.message)
    
    