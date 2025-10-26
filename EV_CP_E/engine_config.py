import argparse

class EngineConfig:
    def __init__(self):
        args = EngineConfig._get_engine_config()
        
        self.kafka_ip = args['kafka_ip']
        self.kafka_port = args['kafka_port']
        self.server_ip = args['server_ip']
        self.server_port = args['server_port']
        self.location = args['location']
        self.price = args['price']

    @staticmethod
    def _get_engine_config():
        parser = argparse.ArgumentParser()
        parser.add_argument('--kafka-ip', type=str, required=True, help='Kafka server IP')
        parser.add_argument('--kafka-port', type=int, required=True, help='Kafka server port')
        parser.add_argument('--server-ip', type=str, required=True, help='IP where monitor server is deployed')
        parser.add_argument('--server-port', type=int, required=True, help='Port where monitor server is deployed')
        parser.add_argument('--location', type=str, required=False, help='CP location')
        parser.add_argument('--price', type=float, required=False, help='CP price of supply')
        
        args = vars(parser.parse_args())
        return args