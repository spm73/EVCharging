from confluent_kafka import Consumer, KafkaError, KafkaException, TIMESTAMP_NOT_AVAILABLE
from typing import Any
from json import loads

from driver_config import DriverConfig

_SUBSCRIBED_TOPIC = ['supply-data2']

def get_latest_info(config: DriverConfig, supply_id: int) -> dict[str, Any] | None:
    """
    Versión optimizada que detecta cuando ha leído todos los mensajes.
    """
    try:
        # Configuración para consumidor temporal
        temp_conf = {
            'bootstrap.servers': f'{config.kafka_ip}:{config.kafka_port}',
            'group.id': f'{config.driver_id}',
            'auto.offset.reset': 'earliest',
            'enable.auto.commit': True,
            'api.version.request': True
        }
        
        temp_consumer = Consumer(temp_conf)
        temp_consumer.subscribe([_SUBSCRIBED_TOPIC])
        
        # messages = []
        most_recent_message = None
        most_recent_timestamp = None
        empty_polls = 0
        max_empty_polls = 3  # Si 3 polls seguidos están vacíos, terminamos
        
        while empty_polls < max_empty_polls:
            msg = temp_consumer.poll(timeout=1.0)
            
            if msg is None:
                empty_polls += 1
                continue
            
            # Reiniciar contador si recibimos mensaje
            empty_polls = 0
            
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    # Fin de partición alcanzado
                    empty_polls += 1
                    continue
                else:
                    raise KafkaException(msg.error())
            
            # Mensaje válido
            try:
                msg_data = loads(msg.value().decode('utf-8'))
                
                if msg_data.get('supply_id') == supply_id:
                    timestamp = msg.timestamp()[1] if msg.timestamp()[0] != TIMESTAMP_NOT_AVAILABLE else 0
                    if timestamp > most_recent_timestamp:
                        most_recent_timestamp = timestamp
                        most_recent_message = msg_data
                    # messages.append({
                    #     'data': msg_data,
                    #     'timestamp': timestamp,
                    #     'offset': msg.offset(),
                    #     'partition': msg.partition()
                    # })
                    
            except Exception as e:
                print(f"⚠ Error procesando mensaje: {e}")
                continue
        
        temp_consumer.close()
        
        if most_recent_message:
            return most_recent_message

        # if messages:
        #     latest = max(messages, key=lambda x: x['timestamp'])
        #     return latest['data']
        
        return None
        
    except Exception as e:
        print(f"❌ Error en recuperación: {e}")
        return None