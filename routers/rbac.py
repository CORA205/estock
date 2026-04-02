from fastapi import APIRouter, HTTPException, Depends

from database.database import engine, get_db
from sqlalchemy.orm import Session
from schemas.models import  RoleCreate
from utils.auth import require_admin
from models import database_models



ropes = APIRouter(prefix="/roles_permissions", tags=["roles"])


@ropes.post("/", dependencies=[Depends(require_admin)])
def define_role(role: RoleCreate, db: Session = Depends(get_db)):
    db.add(database_models.Role(**role.model_dump()))
    db.commit()
    db.refresh(role)
    return role
