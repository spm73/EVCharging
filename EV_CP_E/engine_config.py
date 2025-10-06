import argparse

class EngineConfig:
    def __init__(self):
        args = EngineConfig._get_engine_config()
        
        self.kafka_ip = args['kafka-ip']
        self.kafka_port = args['kafka-port']

    @staticmethod
    def _get_engine_config():
        parser = argparse.ArgumentParser()
        parser.add_argument('--kafka-ip', type=str, required=True, help='Kafka server IP')
        parser.add_argument('--kafka-port', type=int, required=True, help='Kafka server port')
        
        args = vars(parser.parse_args())
        return args