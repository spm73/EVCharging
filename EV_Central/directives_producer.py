from json import dumps

from confluent_kafka import Producer

class DirectivesProducer:
    TOPIC_NAME = 'central-directives'
    def __init__(self, kafka_ip: str, kafka_port: int):
        conf = {
            'bootstrap.servers': f'{kafka_ip}:{kafka_port}'
        }
        self.producer = Producer(conf)
        
    def _send_directive(self, target: str, action: str, supply_id: int | None):
        msg = {
            'target': target,
            'action': action,
        }
        
        if supply_id:
            msg['supply_id'] = supply_id
        
        json_msg = dumps(msg)
        self.producer.produce(DirectivesProducer.TOPIC_NAME, value=json_msg)
        
    def start_supply(self, target: str, supply_id: int):
        self._send_directive(target, 'start-supply', supply_id)
        
    def stop_cp(self, target: str):
        self._send_directive(target, 'stop', None)
        
    def stop_all(self):
        self._send_directive('all', 'stop', None)
        
    def resume_cp(self, target: str):
        self._send_directive(target, 'resume', None)
        
    def resume_all(self):
        self._send_directive('all', 'resume', None)