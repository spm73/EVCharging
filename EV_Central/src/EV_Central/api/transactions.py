from fastapi import APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import select

from EV_Central.models.Supply import Supply
from EV_Central.state.Database import Database
from EV_Central.state.CPCollection import CPCollection

router = APIRouter(prefix='/api/transactions')

@router.get("/")
def get_transactions(cp_id: str | None = None):
    cps = CPCollection()
    result = []
    with Session(Database().get_engine()) as session:
        query = select(Supply)
        if cp_id:
            query = query.where(Supply.cp_id == cp_id)
        supplies = session.scalars(query).all()
        for supply in supplies:
            consumption = supply.consumption
            price = float(supply.price) if supply.price is not None else None
            # Para el supply activo, usamos los datos en tiempo real de memoria
            try:
                cp_info = cps.get_cp(supply.cp_id)
                active = cp_info.get_active_supply()
                if active and active.id == supply.id:
                    consumption = active.consumption
                    price = float(active.price)
            except KeyError:
                pass
            result.append({
                "id": supply.id,
                "cp_id": supply.cp_id,
                "driver_id": supply.driver_id,
                "start_date": supply.start_date.isoformat() if supply.start_date else None,
                "consumption": consumption,
                "price": price,
                "is_done": supply.is_done,
            })
    return result