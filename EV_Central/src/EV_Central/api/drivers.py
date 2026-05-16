from fastapi import APIRouter

router = APIRouter(prefix='driver')

@router.get('/')
async def read_all():
    pass
