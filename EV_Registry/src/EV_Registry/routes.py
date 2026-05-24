from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth import verify_certificate, generate_jwt
from models import CP, CPStatus
from database import get_db

class CPRegisterRequest(BaseModel):
    cp_id: str
    location: str
    certificate: str

router = APIRouter(prefix='/registry')

@router.post('/cp')
async def create_cp(request: CPRegisterRequest, db: Session  = Depends(get_db)):
    # 1. Verificar certificado contra la CA
    if not verify_certificate(request.certificate, request.cp_id):
        raise HTTPException(status_code=403, detail="Invalid certificate")

    # 2. Comprobar que no existe ya
    if db.get(CP, request.cp_id):
        raise HTTPException(status_code=409, detail="CP already registered")

    # 3. Guardar en BD
    cp = CP(
        id=request.cp_id,
        location=request.location,
        status=CPStatus.DISCONNECTED,
        price=0.0,
        temperature=0.0
    )
    db.add(cp)
    db.commit()

    # 4. Devolver JWT
    token = generate_jwt(request.cp_id)
    return {"token": token}


@router.delete('/cp/{cp_id}')
async def delete_cp(cp_id: str, db: Session = Depends(get_db)):
    cp = db.get(CP, cp_id)
    if not cp:
        raise HTTPException(status_code=404, detail="CP not found")

    db.delete(cp)
    db.commit()
    return {"message": f"CP {cp_id} deleted successfully"}