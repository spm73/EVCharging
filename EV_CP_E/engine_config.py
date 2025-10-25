import argparse

class EngineConfig:
    def __init__(self):
        args = EngineConfig._get_engine_config()
        
        self.kafka_ip = args['kafka-ip']
        self.kafka_port = args['kafka-port']
        self.server_ip = args['server-ip']
        self.server_port = args['server-port']
        self.location = args['location']

    @staticmethod
    def _get_engine_config():
        parser = argparse.ArgumentParser()
        parser.add_argument('--kafka-ip', type=str, required=True, help='Kafka server IP')
        parser.add_argument('--kafka-port', type=int, required=True, help='Kafka server port')
        parser.add_argument('--server-ip', type=str, required=True, help='IP where monitor server is deployed')
        parser.add_argument('--server-port', type=int, required=True, help='Port where monitor server is deployed')
        parser.add_argument('--location', type=str, required=True, help='CP location')
        
        
        args = vars(parser.parse_args())
        return args