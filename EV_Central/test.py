from supply_req_consumer import SupplyReqConsumer
from json import dumps

if __name__ == '__main__':
    ip = 'localhost'
    port = 9092

    consumer = SupplyReqConsumer(ip, port)
    try:
        req = None
        while not req:
            req = consumer.get_request()
    except KeyboardInterrupt:
        consumer.close()
        exit()


    print(req)
    consumer.close()
