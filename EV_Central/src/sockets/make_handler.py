from jwt import decode, InvalidTokenError
from os import getenv
from communications.sockets import MessageHandler

from ..state.RegistryKey import RegistryKey
from ..state.CPCollection import CPCollection
from ..state.CPInfo import CPInfo
from ..models.CPStatus import CPStatus
from ..state.KafkaManager import KafkaManager
from ..kafka.messages.DriverNotificationMessage import DriverNotificationMessage

def make_handler() -> MessageHandler:
    cp: CPInfo | None = None
    
    def handle_auth(message: str) -> str:
        _, cp_id, jwt_token = message.split('#')
        
        key = RegistryKey().get_key()
        
        try:
            payload = decode(jwt_token, key, algorithms=["HS256"])
            if payload["cp_id"] != cp_id:
                return "AUTH#denied"
        except InvalidTokenError:
            return "AUTH#denied"
        
        cps = CPCollection()
        try:
            cp = cps.get_cp(cp_id)
        except KeyError:
            cp = cps.add_cp(cp_id)
            
        cp.assign_key()
        cp_key = cp.get_key().decode()
        return f"AUTH#accepted#{cp_key}"
    
    def handle_status(message: str) -> str:
        if cp is None:
            return "ERROR#not_authenticated"
        
        _, status_str = message.split('#')
        try:
            status = CPStatus(status_str)
            cp.change_status(status)
            if status == CPStatus.BROKEN_DOWN and \
                cp.is_supplying():
                    producer = KafkaManager().get_factory().create_producer('driver.notifications')
                    producer.send_message(
                        DriverNotificationMessage(
                            cp.get_active_supply().driver_id,
                            'The CP has suffered a failure, your supply will resume once the problem is solved'
                        )
                    )
            return "STATUS#copy"
        except ValueError:
            return "STATUS#invalid"
        
    def handle_bye(message: str) -> str:
        if cp is None:
            return "BYE#Error"
        cp.change_status(CPStatus.DISCONNECTED)
        return "BYE#thanks"
    
    def default(_: str) -> str:
        return "ERROR#message_not_recognized"
        
    handler = MessageHandler(default=default)
    handler.register("AUTH", handle_auth)
    handler.register("STATUS", handle_status)
    handler.register("BYE", handle_bye)
    return handler
        