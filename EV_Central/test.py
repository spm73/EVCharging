from supply_req_consumer import SupplyReqConsumer
from json import dumps

if __name__ == '__main__':
    ip = '192.168.18.218'
    port = 9092

    consumer = SupplyReqConsumer(ip, port)
    try:
        while True:
            req = None
            while not req:
                req = consumer.get_request()
            print(req)
    except KeyboardInterrupt:
        consumer.close()
        exit()


    consumer.close()
