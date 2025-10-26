import argparse

class CentralConfig:
    def __init__(self):
        args = CentralConfig._get_central_config()
        
        self.ip = args['ip']
        self.port = args['port']
        self.kafka_ip = args['kafka-ip']
        self.kafka_port = args['kafka-port']
        self.db_ip = args['db-ip']
        self.db_port = args['db-port']
        

    @staticmethod
    def _get_central_config():
        parser = argparse.ArgumentParser()
        parser.add_argument('--ip', type=str, help='Listening IP', required=True)
        parser.add_argument('--port', type=int, help='Listening port', required=True)
        parser.add_argument('--kafka-ip', type=str, help='Kafka server IP', required=True)
        parser.add_argument('--kafka-port', type=int, help='Kafka server port', required=True)
        parser.add_argument('--db-ip', type=str, help='Database server IP', required=True)
        parser.add_argument('--db-port', type=int, help='Database server port', required=True)
        
        args = vars(parser.parse_args())
        return args
    