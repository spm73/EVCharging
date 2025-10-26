import sys
import select
from confluent_kafka import KafkaException

from engine_config import EngineConfig
from directives_consumer import DirectivesConsumer
from supply_req_producer import SupplyReqProducer
from supply_res_consumer import SupplyResConsumer
from supply_info import SupplyInfo
from monitor_handler import monitor_handler
from monitor_server import MonitorServer
from cp_status import CPStatus
from engine_data import EngineData
from engine_app import *

def handle_directives(directives_consumer: DirectivesConsumer, cp_status: CPStatus, supply_info: SupplyInfo | None) -> int | None:
    try:
        directive = directives_consumer.get_directive()
    except KafkaException as e:
        error = str(e.args[0])
        print(f"Error receiving response {error}")
        return
    
    if not directive:
        return None
    
    match directive['action']:
        case 'start-supply' if cp_status.is_active():
            cp_status.set_waiting_for_supplying()
            return directive['supply_id']
        case 'stop' if cp_status.is_active() or cp_status.is_waiting_for_supply():
            cp_status.set_stopped()
        case 'stop' if cp_status.is_supplying() and supply_info:
            supply_info.send_ticket()
        case 'resume' if cp_status.is_stopped():
            cp_status.set_active()
            # entrar en la interfaz de Nico


def main():
    config = EngineConfig()
    monitor_server = MonitorServer(config.server_ip, config.server_port)
    monitor_server.listen()
    cp_data = EngineData()

    monitor_server.accept(monitor_handler, cp_data)
    # cp_status.set_active() not necessary I believe
    directives_consumer = DirectivesConsumer(config.kafka_ip, config.kafka_port, cp_data.id)
    supply_info = None
    supply_id = None
    
    running = True
    print("The engine is waiting for a supply...")
    print("- To turn off press letter \"q\"")
    print("- If you want start a supply without driver press \"ENTER\"")
    while running: # is_active

        #!!!!!!!!primero que compruebe si ha habido un error, si lo hay para el cp¡¡¡¡¡¡¡¡

        #si se pulsa una tecla entra
        if select.select([sys.stdin], [], [], 0)[0]:
            key = sys.stdin.read(1)
            #si enter
            if key == '\n':
                supply_request = SupplyReqProducer(config.kafka_ip, config.kafka_port)
                supply_response = SupplyResConsumer(config.kafka_ip, config.kafka_port, cp_data.id)
                supply_request.send_request(cp_data.id)
                print("Central: checking if CP is available for supply...")
                response = None
                while not response:
                    try:
                        response = supply_response.get_response()
                    except KafkaException as e:
                        error = str(e.args[0])
                        print(f"Error receiving response {error}")
                        continue
                    
                supply_response.close()
                if response['status'] == 'denied':
                    print("Supply was denied")
                    print(f"Reason: {response['reason']}")
                    # limpiar la pantalla
                    print("The engine is waiting for a supply...")
                    print("- To turn off press letter \"q\"")
                    print("- If you want start a supply without driver press \"ENTER\"")
                    continue
                
                possible_supply_id = None
                while not possible_supply_id: # refinar bucle para que pasa si le llega otro tipo de directivas
                    possible_supply_id = handle_directives(directives_consumer, cp_data.status, supply_info)
                supply_id = possible_supply_id if possible_supply_id else supply_id
                if supply_id:
                    print(f"____________________Driver connected___________________")
                    print(" - Do you want to plug the car?(n/y | default y)")
                    response = input("---> ")
                    if response == "n":
                        # limpiar la pantalla
                        print("The engine is waiting for a supply...")
                        print("- To turn off press letter \"q\"")
                        print("- If you want start a supply without driver press \"ENTER\"")
                        continue
                    
                    cp_data.status.set_supplying()
                    supply_info = SupplyInfo(config.kafka_ip, config.kafka_port, supply_id)
                    time_ini = time.time()
                    print("Press \'Enter\' to unplug:")
                    while cp_data.status.is_supplying():
                        time_plug = time.time() - time_ini
                        supply_info.send_info()
                        amount = supply_info.get_consumption()
                        cost = supply_info.get_cost()
                        print(f"\r{' ' * 60}\rTime = {time_plug:.2f}s    Amount = {amount:.4f}kwh   Cost = {cost:.4f}€", end="")
                        sys.stdout.flush()

                        if select.select([sys.stdin], [], [], 0)[0]:
                            input()  # limpia el buffer
                            print("\n")
                            cp_data.status.set_active()

                    supply_info.send_ticket()
                    print("\"\"\" Thank you for using our service. :)\"\"\"")
                    
                print("\n")
                #llamar supply_interface()

            #si q
            elif key.lower() == 'q':
                return
            
        #!!!!!!!!aqui poner el if para leer del kafka ¡¡¡¡¡¡¡¡
        
        
    
    # menu para elegir si hacer el suministro



if __name__ == '__main__':
    main()
