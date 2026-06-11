from communications.kafka import Message
from sqlalchemy.orm import Session

from EV_Central.models.Supply import Supply
from EV_Central.state.CPCollection import CPCollection
from EV_Central.state.KafkaManager import KafkaManager
from EV_Central.state.Database import Database
from EV_Central.audit.audit import audit
from EV_Central.kafka.messages import *
from EV_Central.models.Driver import Driver

def driver_request_handler(request: SupplyRequestMessage) -> None:
    factory = KafkaManager().get_factory()
    notification_producer = factory.create_producer('supply.request.notifications')
    response_producer = factory.create_producer('supply.response')
    
    audit(request.ip, 'SUPPLY REQUEST', f"Driver {request.driver_id} requests supply in CP {request.cp_id}")
    
    notification_producer.send_message(
        SupplyRequestNotificationMessage(request.driver_id, 'Checking CP existence...')
    )
    cps = CPCollection()
    requested_cp = None
    try:
        requested_cp = cps.get_cp(request.cp_id)
    except KeyError as e:
        audit(request.ip, 'SUPPLY DENIED', f"CP {request.cp_id} not found")
        response_producer.send_message(
            SupplyResponseMessage(request.driver_id, 'denied', str(e), None)
        )
        return
    
    notification_producer.send_message(
        SupplyRequestNotificationMessage(request.driver_id, 'Checking CP availability...')
    )
    if requested_cp.is_available():
        cp_command_producer = factory.create_producer('cp.commands')
        notification_producer.send_message(
            SupplyRequestNotificationMessage(request.driver_id, 'Locking CP for supply...')
        )
        # cp_command_producer.send_message(
        #     CentralCommandMessage(requested_cp.get_id(), 'lock')
        # )
        cp_command_producer.send_message(
            EncryptedMessage(
                requested_cp.get_id(),
                CentralCommandMessage(requested_cp.get_id(), 'lock')
            )
        )
        supply = None
        with Session(Database().get_engine()) as session:
            driver = session.get(Driver, request.driver_id)
            if not driver:
                driver = Driver(id=request.driver_id)
                session.add(driver)
                session.commit()
            supply = Supply(
                cp_id=request.cp_id,
                driver_id=request.driver_id
            )
            session.add(supply)
            session.commit()
            session.refresh(supply)
        start_supply_producer = factory.create_producer('cp.start-supply')
        # start_supply_producer.send_message(
        #     StartSupplyMessage(supply.id)
        # )
        start_supply_producer.send_message(
            EncryptedMessage(
                requested_cp.get_id(),
                StartSupplyMessage(supply.id)
            )
        )
        requested_cp.start_supply(supply.id, request.driver_id)
        response_producer.send_message(
            SupplyResponseMessage(request.driver_id, 'accepted', None, supply.id)
        )
        audit(request.ip, 'SUPPLY ACCEPTED', f"Supply {supply.id} started for Driver {request.driver_id} on CP {request.cp_id}")
    else:
        response_producer.send_message(
            SupplyResponseMessage(request.driver_id, 'denied', 'CP cannot attend a supply', None)
        )
        audit(request.ip, 'SUPPLY DENIED', f" CP {request.cp_id} is not available")
        

def cp_request_handler(request: SupplyRequestMessage) -> None:
    factory = KafkaManager().get_factory()
    cp = CPCollection().get_cp(request.cp_id)
    audit(request.ip, 'SUPPLY REQUEST', f"CP {request.cp_id} requests a supply")
    supply = None
    with Session(Database().get_engine()) as session:
        driver = session.get(Driver, request.driver_id)
        if not driver:
            driver = Driver(id=request.driver_id)
            session.add(driver)
            session.commit()
        supply = Supply(
            cp_id=request.cp_id,
            driver_id=request.driver_id
        )
        session.add(supply)
        session.commit()
        session.refresh(supply)
    cp.start_supply(supply.id, request.driver_id)
    start_supply_producer = factory.create_producer('cp.start-supply')
    # start_supply_producer.send_message(
    #     StartSupplyMessage(supply.id)
    # )
    start_supply_producer.send_message(
        EncryptedMessage(
            request.cp_id,
            StartSupplyMessage(supply.id)
        )
    )
    audit(request.ip, 'SUPPLY ACCEPTED', f"Supply {supply.id} started on CP {request.cp_id}")
    
    
def resend_telemetry(telemetry: SupplyTelemetryMessage) -> None:
    factory = KafkaManager().get_factory()
    producer = factory.create_producer('supply.telemetry.users')
    
    with Session(Database().get_engine()) as session:
        supply = session.get(Supply, telemetry.supply_id)
        if supply is None or supply.is_done:
            print(f"Supply {telemetry.supply_id} not registered or already done")
            return
            
        supply.consumption = telemetry.consumption
        supply.price = telemetry.price
        
        if telemetry.is_ticket():
            supply.is_done = True
            
        session.commit()

    cp_collection = CPCollection()
    cp = cp_collection.get_cp_by_supply_id(telemetry.supply_id)
    if cp is not None:
        cp.update_supply(telemetry.consumption, telemetry.price)
        if telemetry.is_ticket():
            cp.end_supply()
        
    producer.send_message(telemetry)