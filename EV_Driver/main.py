import sys
from time import sleep
from confluent_kafka import KafkaException

from driver_config import DriverConfig
from supply_req_producer import SupplyReqProducer
from supply_res_consumer import SupplyResConsumer
from supply_info_consumer import SupplyInfoConsumer

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
        print('Supplied denied')
        print(f'Reason: {response['reason']}')
        return None
    
    res_consumer.close()
    return response['supply_id']


def supplying(supply_id: int, kafka_ip: str, kafka_port: int):
    info_consumer = SupplyInfoConsumer(kafka_ip, kafka_port, supply_id)
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
                supplying(supply_id, driver_config.kafka_ip, driver_config.kafka_port)
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
