from json import dumps

from confluent_kafka import Producer

class SupplyResProducer:
    TOPIC_NAME = 'supply-res'
    def __init__(self, kafka_ip: str, kafka_port: int):
        conf = {
            'bootstrap.servers': f'{kafka_ip}:{kafka_port}'
        }
        self.producer = Producer(conf)
        
    def send_response(self, drive_id: str, status: bool, reason: str | None, supply_id: int | None):
        status_msg = "authorized" if status else "denied"
        msg_content = {
            'applicant_id': drive_id,
            'status': status_msg,
            'reason': reason,
            'supply_id': supply_id
        }
        msg = dumps(msg_content)
        self.producer.produce(SupplyResProducer.TOPIC_NAME, value=msg)