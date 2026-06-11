from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from EV_Central.state.CPCollection import CPCollection
from EV_Central.state.KafkaManager import KafkaManager
from EV_Central.state.Database import Database
from EV_Central.models.CP import CP
from EV_Central.models.CPStatus import CPStatus
from EV_Central.kafka.messages import CentralCommandMessage

router = APIRouter(prefix="/api/cps")

@router.get("/")
def get_cps(status: str | None = None):
    cps = CPCollection()
    with Session(Database().get_engine()) as session:
        db_cps = session.scalars(select(CP)).all()
        result = []
        for cp in db_cps:
            try:
                cp_info = cps.get_cp(cp.id)
                cp_status = cp_info.get_status().value
                temperature = cp_info.get_temp()
                active_supply = cp_info.get_active_supply().__dict__ if cp_info.get_active_supply() else None
            except KeyError:
                cp_status = cp.status.value
                temperature = float(cp.temperature)
                active_supply = None

            if status and cp_status != status:
                continue

            result.append({
                "id": cp.id,
                "location": cp.location,
                "price": float(cp.price),
                "status": cp_status,
                "temperature": temperature,
                "active_supply": active_supply
            })
        return result

@router.post("/{cp_id}/weather-alert")
def weather_alert(cp_id: str):
    try:
        _ = CPCollection().get_cp(cp_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"CP {cp_id} not found")
    producer = KafkaManager().get_factory().create_producer('cp.commands')
    producer.send_message(CentralCommandMessage(cp_id, 'stop'))
    return {"detail": f"Weather alert sent to CP {cp_id}"}

@router.delete("/{cp_id}/weather-alert")
def cancel_weather_alert(cp_id: str):
    try:
        _ = CPCollection().get_cp(cp_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"CP {cp_id} not found")
    producer = KafkaManager().get_factory().create_producer('cp.commands')
    producer.send_message(CentralCommandMessage(cp_id, 'resume'))
    return {"detail": f"Weather alert cancelled for CP {cp_id}"}

@router.post("/{cp_id}/stop")
def stop_cp(cp_id: str):
    try:
        _ = CPCollection().get_cp(cp_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"CP {cp_id} not found")
    producer = KafkaManager().get_factory().create_producer('cp.commands')
    producer.send_message(CentralCommandMessage(cp_id, 'stop'))
    return {"detail": f"Stop command sent to CP {cp_id}"}

@router.post("/{cp_id}/resume")
def resume_cp(cp_id: str):
    try:
        _ = CPCollection().get_cp(cp_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"CP {cp_id} not found")
    producer = KafkaManager().get_factory().create_producer('cp.commands')
    producer.send_message(CentralCommandMessage(cp_id, 'resume'))
    return {"detail": f"Resume command sent to CP {cp_id}"}

@router.post("/stop-all")
def stop_all_cps():
    cps = CPCollection()
    producer = KafkaManager().get_factory().create_producer('cp.commands')
    for cp_id in cps.get_active_cps_ids():
        producer.send_message(CentralCommandMessage(cp_id, 'stop'))
    return {"detail": "Stop command sent to all active CPs"}

@router.post("/resume-all")
def resume_all_cps():
    cps = CPCollection()
    producer = KafkaManager().get_factory().create_producer('cp.commands')
    for cp_id in cps.get_active_cps_ids():
        producer.send_message(CentralCommandMessage(cp_id, 'resume'))
    return {"detail": "Resume command sent to all active CPs"}

@router.delete("/{cp_id}/key")
def delete_cp_key(cp_id: str):
    try:
        cp = CPCollection().get_cp(cp_id)
        cp.delete_key()
    except KeyError:
        raise HTTPException(status_code=404, detail=f"CP {cp_id} not found")
    return {"detail": f"Symmetric key deleted for CP {cp_id}"}