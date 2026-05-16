from fastapi import APIRouter

router = APIRouter(prefix='events')

@router.get('/')
async def read_all(ip: str | None = None, action: str | None = None):
    pass
