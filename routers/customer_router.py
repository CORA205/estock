from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import select, or_

from utils.auth import require_admin, get_current_user

from database.database import get_db
from models import database_models
from schemas.models import CustomerCreate, CustomerPatch

custom = APIRouter(prefix="/customers", tags=["Customers"], dependencies=[Depends(get_current_user)])


@custom.get("/")
def all_customers(db: Session = Depends(get_db)):
    stmt = select(database_models.Customer)
    return db.scalars(stmt).all()


@custom.get("/search/{name}")
def get_customer_by_name(name: str, db: Session = Depends(get_db)):
    stmt = (
        select(database_models.Customer)
        .options(joinedload(database_models.Customer.orders))
        .where(
            or_(
                database_models.Customer.firstname == name,
                database_models.Customer.lastname == name
            )
        )
    )
    customer = db.scalars(stmt).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Aucun client trouvé avec le nom '{name}'")
    return customer


@custom.get("/{id}")
def get_customer(id: int, db: Session = Depends(get_db)):
    stmt = select(database_models.Customer).where(database_models.Customer.id == id)
    data = db.scalars(stmt).first()
    if not data:
        raise HTTPException(status_code=404, detail=f"Client {id} introuvable")
    return data


@custom.get("/{id}/orders")
def get_customer_orders(id: int, db: Session = Depends(get_db)):
    """Récupère toutes les commandes d'un client avec leurs items."""
    stmt = (
        select(database_models.Customer)
        .options(
            joinedload(database_models.Customer.orders)
            .joinedload(database_models.Order.items)
        )
        .where(database_models.Customer.id == id)
    )
    customer = db.scalars(stmt).first()
    if not customer:
        raise HTTPException(status_code=404, detail=f"Client {id} introuvable")
    return {
        "customer_id": customer.id,
        "firstname": customer.firstname,
        "lastname": customer.lastname,
        "orders": customer.orders
    }


@custom.post("/", status_code=201)
def create_customer(customer: CustomerCreate, db: Session = Depends(get_db)):
    # Vérifier que le manager existe
    manager = db.scalars(
        select(database_models.User).where(database_models.User.id == customer.manager_id)
    ).first()
    if not manager:
        raise HTTPException(status_code=404, detail=f"Manager {customer.manager_id} introuvable")

    new_customer = database_models.Customer(**customer.model_dump())
    db.add(new_customer)
    db.commit()
    db.refresh(new_customer)
    return new_customer


@custom.put("/{id}")
def update_customer(id: int, customer: CustomerCreate, db: Session = Depends(get_db)):
    stmt = select(database_models.Customer).where(database_models.Customer.id == id)
    data = db.scalars(stmt).first()
    if not data:
        raise HTTPException(status_code=404, detail=f"Client {id} introuvable")

    for key, value in customer.model_dump().items():
        setattr(data, key, value)

    db.commit()
    db.refresh(data)
    return data


@custom.patch("/{id}")
def patch_customer(id: int, customer: CustomerPatch, db: Session = Depends(get_db)):
    stmt = select(database_models.Customer).where(database_models.Customer.id == id)
    data = db.scalars(stmt).first()
    if not data:
        raise HTTPException(status_code=404, detail=f"Client {id} introuvable")

    for key, value in customer.model_dump(exclude_unset=True).items():
        setattr(data, key, value)

    db.commit()
    db.refresh(data)
    return data


@custom.delete("/{id}", dependencies=[Depends(require_admin)])
def delete_customer(id: int, db: Session = Depends(get_db)):
    stmt = select(database_models.Customer).where(database_models.Customer.id == id)
    data = db.scalars(stmt).first()
    if not data:
        raise HTTPException(status_code=404, detail=f"Client {id} introuvable")

    db.delete(data)
    db.commit()
    return {"detail": f"Client {id} supprimé"}