from json import dumps

from confluent_kafka import Producer

class SupplyResProducer:
    TOPIC_NAME = 'supply-error'
    def __init__(self, kafka_ip: str, kafka_port: int):
        conf = {
            'bootstrap.servers': f'{kafka_ip}:{kafka_port}'
        }
        self.producer = Producer(conf)
        
    def send_error(self, supply_id: int):
        msg_content = {
            'supply_id': supply_id,
            'msg': 'Engine has closed down abruptly, we are sorry'
        }
        msg = dumps(msg_content)
        self.producer.produce(SupplyResProducer.TOPIC_NAME, value=msg)
        self.producer.flush()