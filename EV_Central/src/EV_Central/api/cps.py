from fastapi import APIRouter

from ..models.CPStatus import CPStatus

router = APIRouter(prefix="cps")

@router.get('/')
async def read_all(cp_status: str | None = None):
    pass


@router.post('/{cp_id}/temperature')
async def update_temperature(cp_id: str):
    pass

