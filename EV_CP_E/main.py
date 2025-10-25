from engine_config import EngineConfig
from directives_consumer import DirectivesConsumer
from supply_req_producer import SupplyReqProducer
from supply_res_consumer import SupplyResConsumer
from supply_info_producer import SupplyInfoProducer
from monitor_handler import monitor_handler
from monitor_server import MonitorServer
from cp_status import CPStatus
from cp_id import CPId

def handle_directives(directives_consumer: DirectivesConsumer, cp_status: CPStatus):
    directive = directives_consumer.get_directive()
    match directive['action']:
        case 'stop' if cp_status.is_active() or cp_status.is_waiting_for_supply():
            cp_status.set_stopped()
        case 'stop' if cp_status.is_supplying():
            # A solucionar
            supply_info_producer.send_ticket()
        case 'resume' if cp_status.is_stopped():
            cp_status.set_active()
        case 'start-supply' if cp_status.is_active():
            cp_status.set_waiting_for_supplying()
            # entrar en la interfaz de Nico


def main():
    config = EngineConfig()
    monitor_server = MonitorServer(config.server_ip, config.server_port)
    monitor_server.listen()
    cp_status = CPStatus()
    cp_id = CPId()

    monitor_server.accept(monitor_handler, cp_status, cp_id, config.location)
    # cp_status.set_active() not necessary I believe
    directives_consumer = DirectivesConsumer(config.kafka_ip, config.kafka_port, cp_id)
    supply_info_producer = SupplyInfoProducer(config.kafka_ip, config.kafka_port)
    
    running = True
    while running:
        handle_directives(directives_consumer, cp_status)


    supply_request = SupplyReqProducer(config.kafka_ip, config.kafka_port)
    supply_response = SupplyResConsumer(config.kafka_ip, config.kafka_port, cp_id)
    
    # menu para elegir si hacer el suministro



if __name__ == '__main__':
    main()
