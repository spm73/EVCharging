from json import dumps

from confluent_kafka import Producer

class SupplyReqProducer:
    TOPIC_NAME = 'supply-req'
    def __init__(self, kafka_ip: str, kafka_port: int):
        conf = {
            'bootstrap.servers': f'{kafka_ip}:{kafka_port}'
        }
        self.producer = Producer(conf)
        
    def send_request(self, cp_id: str):
        msg = {
            'cp_id': cp_id
        }
        json_msg = dumps(msg)
        self.producer.produce(SupplyReqProducer.TOPIC_NAME, value=json_msg)