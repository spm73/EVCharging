import argparse

class MonitorConfig:
    def __init__(self):
        args = MonitorConfig._get_monitor_config()
        
        self.cp_ip = args['id']
        self.central_ip = args['central-ip']
        self.central_port = args['central-port']
        self.engine_ip = args['engine-ip']
        self.engine_port = args['engine-port']

    @staticmethod
    def _get_monitor_config():
        parser = argparse.ArgumentParser()
        
        parser.add_argument('--id', type=int, required=True, help='Charging point ID')
        parser.add_argument('--central-ip', type=str, required=True, help='Central server IP')
        parser.add_argument('--central-port', type=int, required=True, help='Central server port')
        parser.add_argument('--engine-ip', type=str, required=True, help='Engine IP')
        parser.add_argument('--engine-port', type=int, required=True, help='Engine port')
        
        args = vars(parser.parse_args())
        return args