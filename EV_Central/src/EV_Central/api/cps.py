from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..state.CPCollection import CPCollection
from ..state.KafkaManager import KafkaManager
from ..state.Database import Database
from ..models.CP import CP
from ..models.CPStatus import CPStatus
from ..kafka.messages import CentralCommandMessage

router = APIRouter(prefix="/api/cps")

@router.get("/")
def get_cps(status: str | None = None):
    cps = CPCollection()
    with Session(Database().get_engine()) as session:
        db_cps = session.scalars(select(CP)).all()
        result = []
        for cp in db_cps:
            cp_info = cps.get_cp(cp.id)
            cp_status = cp_info.get_status()
            if status and cp_status != CPStatus(status):
                continue
            result.append({
                "id": cp.id,
                "location": cp.location,
                "price": float(cp.price),
                "status": cp_status.value,
                "temperature": cp_info.get_temp(),
                "active_supply": cp_info.get_active_supply().__dict__ if cp_info.get_active_supply() else None
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