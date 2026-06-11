from .messages import *
from communications.kafka.KafkaNotifier import KafkaNotifier, M
from ..system.events import *
from ..system.event_bus import EVENT_QUEUE

def cp_listing_handler (message: ActiveCPListingMessage) -> None:
    new_cp_list = message.active_cps
    event = SystemEvent(intention=Intention.UPDATE_CPS, data=new_cp_list)
    
    EVENT_QUEUE.put(event)

def response_handler (message: SupplyResponseMessage) -> None:
    if message.status == "accepted":
        event = SystemEvent(intention=Intention.ACCEPTED_RESPONSE, data=message.supply_id)
        EVENT_QUEUE.put(event)
        return

    else:
        event = SystemEvent(intention=Intention.DENIED_RESPONSE, data=message.reason)
        EVENT_QUEUE.put(event)
        return

def telemetry_info_handler (message: SupplyTelemetryMessage) -> None:
    if message.type == "supplying":
        event = SystemEvent(intention=Intention.TELEMETRY_INFO, data=message)
        EVENT_QUEUE.put(event)
        return

    else:
        event = SystemEvent(intention=Intention.TELEMETRY_TICKET, data=message)
        EVENT_QUEUE.put(event)
        return

def request_notification_handler (message: SupplyRequestNotificationMessage) -> None:
    event = SystemEvent(intention=Intention.NOTIFICATIONS, data=message.message)
    
    EVENT_QUEUE.put(event)

def kafka_error_handler (message: SupplyErrorMessage) -> None:
    event = SystemEvent(intention=Intention.KAFKA_ERROR, data=message.error_msg)
    
    EVENT_QUEUE.put(event)
