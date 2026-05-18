from fastapi import APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import select

from ..models.Supply import Supply
from ..state.Database import Database
from ..state.CPCollection import CPCollection

router = APIRouter(prefix='/api/transactions')

@router.get("/")
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