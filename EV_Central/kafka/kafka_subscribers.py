from communications.kafka import Message
from sqlalchemy.orm import Session

from ..models.Supply import Supply
from ..state.CPCollection import CPCollection
from ..state.KafkaManager import KafkaManager
from ..state.Database import Database
from .messages import *

def request_handler(request: Message) -> None:
    if not isinstance(request, SupplyRequestMessage):
        print("Someone put the wrong message in the wrong topic")
        return
    
    factory = KafkaManager().get_factory()
    notification_producer = factory.create_producer('supply.request.notification')
    response_producer = factory.create_producer('supply.response')
    notification_producer.send_message(
        SupplyRequestNotificationMessage(request.driver_id, 'Checking CP existence...')
    )
    cps = CPCollection()
    requested_cp = None
    try:
        requested_cp = cps.get_cp(request.cp_id)
    except KeyError as e:
        response_producer.send_message(
            SupplyResponseMessage(request.driver_id, 'denied', str(e), None)
        )
        return
    
    notification_producer.send_message(
        SupplyRequestNotificationMessage(request.driver_id, 'Checking CP availability...')
    )
    if requested_cp.is_available():
        supply = None
        with Session(Database().get_engine()) as session:
            supply = Supply(
                cp_id=request.cp_id,
                driver_id=request.driver_id
            )
            session.add(supply)
            session.commit()
            session.refresh(supply)
        requested_cp.start_supply(supply.id)
        response_producer.send_message(
            SupplyResponseMessage(request.driver_id, 'accepted', None, supply.id)
        )
    else:
        response_producer.send_message(
            SupplyResponseMessage(request.driver_id, 'denied', 'CP cannot attend a supply', None)
        )
    
def resend_telemetry(telemetry: Message) -> None:
    if not isinstance(telemetry, SupplyTelemetryMessage):
        print("Someone put the wrong message in the wrong topic")
        return
    
    factory = KafkaManager().get_factory()
    producer = factory.create_producer('supply.telemetry.users')
    cp_collection = CPCollection()
    cp = cp_collection.get_cp_by_supply_id(telemetry.supply_id)
    if cp is None:
        print("Supply not registered")
        return
    cp.update_supply(telemetry.consumption, telemetry.price)
    if telemetry.is_ticket():
        cp_collection.end_supply(cp.get_id())
        
    producer.send_message(telemetry)