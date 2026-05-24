from fastapi import APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..state.Database import Database
from ..models.Event import Event

router = APIRouter(prefix="/api/events")

@router.get("/")
def get_events(ip: str | None = None, action: str | None = None):
    with Session(Database().get_engine()) as session:
        query = select(Event)
        if ip:
            query = query.where(Event.ip == ip)
        if action:
            query = query.where(Event.action == action)
        events = session.scalars(query).all()
        return [{"id": e.id, "timestamp": e.timestamp, "ip": e.ip, "action": e.action, "description": e.description} for e in events]