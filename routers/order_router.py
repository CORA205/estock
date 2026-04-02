from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from utils.auth import get_current_user
from database.database import get_db
from models import database_models
from schemas.models import OrderCreate

command = APIRouter(prefix="/orders", tags=["Orders"], dependencies=[Depends(get_current_user)])


@command.get("/")
def all_orders(db: Session = Depends(get_db)):
    stmt = select(database_models.Order)
    return db.scalars(stmt).all()


@command.get("/{id}")
def get_order(id: int, db: Session = Depends(get_db)):
    stmt = select(database_models.Order).where(database_models.Order.id == id)
    data = db.scalars(stmt).first()
    if not data:
        raise HTTPException(status_code=404, detail="Commande introuvable")
    return data


@command.get("/customer/{customer_id}")
def get_orders_by_customer(customer_id: int, db: Session = Depends(get_db)):
    stmt = select(database_models.Order).where(database_models.Order.customer_id == customer_id)
    data = db.scalars(stmt).all()
    if not data:
        raise HTTPException(status_code=404, detail="Aucune commande pour ce client")
    return data


@command.post("/", status_code=201)
def create_order(order: OrderCreate, db: Session = Depends(get_db)):
    # Vérifier que le client existe
    customer = db.scalars(
        select(database_models.Customer).where(database_models.Customer.id == order.customer_id)
    ).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Client introuvable")

    new_order = database_models.Order(**order.model_dump())
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order


@command.delete("/{id}")
def delete_order(id: int, db: Session = Depends(get_db)):
    stmt = select(database_models.Order).where(database_models.Order.id == id)
    data = db.scalars(stmt).first()
    if not data:
        raise HTTPException(status_code=404, detail="Commande introuvable")

    db.delete(data)
    db.commit()
    return {"detail": "Commande supprimée"}