import argparse

class DriverConfig:
    def __init__(self):
        args = DriverConfig._get_driver_config()
        
        self.client_id = args['id']
        self.kafka_ip = args['kafka-ip']
        self.kafka_port = args['kafka-port']

    @staticmethod
    def _get_driver_config():
        parser = argparse.ArgumentParser()
        parser.add_argument('--id', type=int, required=True, help='ID of client')
        parser.add_argument('--kafka-ip', type=str, required=True, help='Kafka server IP')
        parser.add_argument('--kafka-port', type=int, required=True, help='Kafka server port')
        
        args = vars(parser.parse_args())
        return args
    