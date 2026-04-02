from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from utils.auth import require_admin, get_current_user
from database.database import get_db
from models import database_models
from schemas.models import OrderItemCreate

items = APIRouter(prefix="/order-items", tags=["Order Items"], dependencies=[Depends(get_current_user)])


@items.get("/")
def all_order_items(db: Session = Depends(get_db)):
    stmt = select(database_models.OrderItem)
    return db.scalars(stmt).all()


@items.get("/{id}")
def get_order_item(id: int, db: Session = Depends(get_db)):
    stmt = select(database_models.OrderItem).where(database_models.OrderItem.id == id)
    data = db.scalars(stmt).first()
    if not data:
        raise HTTPException(status_code=404, detail="Item introuvable")
    return data


@items.get("/order/{order_id}")
def get_items_by_order(order_id: int, db: Session = Depends(get_db)):
    stmt = select(database_models.OrderItem).where(database_models.OrderItem.order_id == order_id)
    data = db.scalars(stmt).all()
    if not data:
        raise HTTPException(status_code=404, detail="Aucun item pour cette commande")
    return data


@items.post("/", status_code=201)
def create_order_item(item: OrderItemCreate, db: Session = Depends(get_db)):
    # Vérifier que la commande existe
    order = db.scalars(
        select(database_models.Order).where(database_models.Order.id == item.order_id)
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Commande introuvable")

    # Vérifier que le produit existe
    product = db.scalars(
        select(database_models.Product).where(database_models.Product.id == item.product_id)
    ).first()
    if not product:
        raise HTTPException(status_code=404, detail="Produit introuvable")

    new_item = database_models.OrderItem(**item.model_dump())
    db.add(new_item)
    db.commit()
    db.refresh(new_item)
    return new_item


@items.patch("/{id}")
def patch_order_item(id: int, item: OrderItemCreate, db: Session = Depends(get_db)):
    stmt = select(database_models.OrderItem).where(database_models.OrderItem.id == id)
    data = db.scalars(stmt).first()
    if not data:
        raise HTTPException(status_code=404, detail="Item introuvable")

    for key, value in item.model_dump(exclude_unset=True).items():
        setattr(data, key, value)

    db.commit()
    db.refresh(data)
    return data


@items.delete("/{id}")
def delete_order_item(id: int, db: Session = Depends(get_db)):
    stmt = select(database_models.OrderItem).where(database_models.OrderItem.id == id)
    data = db.scalars(stmt).first()
    if not data:
        raise HTTPException(status_code=404, detail="Item introuvable")

    db.delete(data)
    db.commit()
    return {"detail": "Item supprimé"}