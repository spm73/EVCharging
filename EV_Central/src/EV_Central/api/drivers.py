from fastapi import APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import select

from EV_Central.state.Database import Database
from EV_Central.state.CPCollection import CPCollection
from EV_Central.models.Driver import Driver
from EV_Central.models.Supply import Supply

router = APIRouter(prefix="/api/drivers")

@router.get("/")
def get_drivers():
    with Session(Database().get_engine()) as session:
        drivers = session.scalars(select(Driver)).all()
        return [{"id": d.id, "active_supply": next(
            ({"id": s.id, "cp_id": s.cp_id} for s in d.supplies if not s.is_done), None
        )} for d in drivers]

@router.get("/transactions")
def get_transactions(cp_id: str | None = None):
    cps = CPCollection()
    result = []
    with Session(Database().get_engine()) as session:
        query = select(Supply).where(Supply.is_done == False)
        if cp_id:
            query = query.where(Supply.cp_id == cp_id)
        supplies = session.scalars(query).all()
        for supply in supplies:
            cp_info = cps.get_cp(supply.cp_id)
            active = cp_info.get_active_supply()
            result.append({
                "id": supply.id,
                "cp_id": supply.cp_id,
                "driver_id": supply.driver_id,
                "consumption": active.consumption if active else None,
                "price": float(active.price) if active else None,
            })
    return result