from engine_config import EngineConfig
from directives_consumer import DirectivesConsumer
from supply_req_producer import SupplyReqProducer
from supply_res_consumer import SupplyResConsumer
from supply_info_producer import SupplyInfoProducer
from monitor_handler import monitor_handler
from monitor_server import MonitorServer
from cp_status import CPStatus

def main():
    config = EngineConfig()
    monitor_server = MonitorServer(config.server_ip, config.server_port)
    monitor_server.listen()
    cp_status = CPStatus()
    cp_id = 'Random'

    running = True
    while running:
        monitor_server.accept(monitor_handler, cp_status, cp_id)
        
    while otro:
        pass
    # conseguir el cp_id

    directives_consumer = DirectivesConsumer(config.kafka_ip, config.kafka_port, cp_id)
    supply_request = SupplyReqProducer(config.kafka_ip, config.kafka_port)
    supply_response = SupplyResConsumer(config.kafka_ip, config.kafka_port, cp_id)
    
    # menu para elegir si hacer el suministro



if __name__ == '__main__':
    main()
