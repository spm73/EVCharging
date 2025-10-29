from supply_req_producer import SupplyReqProducer

if __name__ == '__main__':
    ip = 'localhost'
    port = 9092

    producer = SupplyReqProducer(ip, port)
    producer.send_request('2', 'yo')