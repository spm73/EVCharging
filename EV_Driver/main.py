import sys
from time import sleep
from confluent_kafka import KafkaException
import os

from driver_config import DriverConfig
from supply_req_producer import SupplyReqProducer
from supply_res_consumer import SupplyResConsumer
from supply_info_consumer import SupplyInfoConsumer
from recover_last_data import get_latest_info

RECOVER_PATH = '/var/recover'

def get_cp_from_file() -> list[str]:
    CPs = []
    with open("cp_list.txt", "r") as archivo:
        for linea in archivo:
            CPs.append(linea.strip())
    return CPs


def ask_supply(cp_id: str, config: DriverConfig) -> int | None:
    req_producer = SupplyReqProducer(config.kafka_ip, config.kafka_port)
    res_consumer = SupplyResConsumer(config.kafka_ip, config.kafka_port, config.client_id)
    
    req_producer.send_request(cp_id, config.client_id)
    response = None
    while not response:
        try:
            response = res_consumer.get_response()
        except KafkaException as e:
            error = str(e.args[0])
            print(f"Error receiving response: {error}")
            continue

    if response['status'] == 'denied':
        print('Supply denied')
        print(f'Reason: {response['reason']}')
        return None
    
    res_consumer.close()
    return response['supply_id']


def check_recover_file(driver_config: DriverConfig) -> int | None:
    file_name = "." + driver_config.client_id
    file_path = os.path.join(RECOVER_PATH, file_name)
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            supply_id = int(f.readline())
            return supply_id
    return None


def create_recover_file(supply_id: int, config: DriverConfig):
    file_name = "." + config.client_id
    file_path = os.path.join(RECOVER_PATH, file_name)
    with open(file_path, 'w') as file:
        file.write(supply_id)


def delete_recover_file(config: DriverConfig):
    file_name = "." + config.client_id
    file_path = os.path.join(RECOVER_PATH, file_name)
    os.remove(file_path)


def supplying(supply_id: int, config: DriverConfig):
    info_consumer = SupplyInfoConsumer(config.kafka_ip, config.kafka_port, supply_id, config.client_id)
    supplying = True 
    while supplying:
        info = None
        try:
            info = info_consumer.get_info()
        except KafkaException as e:
            error = str(e.args[0])
            print(f"Error receiving response: {error}")
            continue
        
        if info and info['type'] == 'ticket':
            supplying = False
            print("Ticket:")
            print(f"Consumption: {info['consumption']}kwh")
            print(f"Price: {info['price']}€")
        elif info and info['type'] == 'supplying':
            amount = info['consumption']
            cost = info['price']
            print(f"\r{' ' * 60}\rConsumption = {amount:.4f}kwh   Price = {cost:.4f}€", end="")
            sys.stdout.flush()


def main():
    driver_config = DriverConfig()
    CPs = get_cp_from_file()

    next_cp = 0
    unchecked_supply_id = check_recover_file(driver_config)
    if unchecked_supply_id:
        most_recent_message = get_latest_info(driver_config, unchecked_supply_id)
        if most_recent_message and most_recent_message['type'] == 'ticket':
            print("Ticket:")
            print(f"Consumption: {most_recent_message['consumption']}kwh")
            print(f"Price: {most_recent_message['price']}€")
        elif most_recent_message and most_recent_message['type'] == 'supplying':
            supplying(unchecked_supply_id, driver_config)


    while True:
        print(f"> These are the existing charging points: ")
        for i in range(len(CPs) - 1):
            print(CPs[i], end= ", " )
        print(CPs[len(CPs) - 1])
        print("_____________________Instructions____________________")
        print(" - If you want to connect to a specific one, write its name.")
        print(" - If you want to connect to the next one in the list, type anything")
        print(" - If you expect to close the application, type \"quit\"")
        cp = input("---> ")
        if cp in CPs:
            print(f"Connecting with CP {cp}...")
            print("Central: checking if CP is available for supply...")
            supply_id = ask_supply(cp, driver_config)
            if supply_id:
                create_recover_file(supply_id, driver_config)
                supplying(supply_id, driver_config)
                delete_recover_file(driver_config)
            #enviar una peticion a central a cp
            next_cp = (CPs.index(cp) + 1) % len(CPs)
        elif cp == "quit":
            break
        else:
            print(f"Connecting with CP {CPs[next_cp]}...")
            #enviar una peticion a central a CPs[next_cp]
            next_cp = (next_cp + 1) % len(CPs)
        sleep(4)


if __name__ == '__main__':
    main()
