from fastapi import APIRouter
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from database.database import engine
from sqlalchemy import select, or_

from models import database_models
from schemas.models import  CustomerCreate, CustomerPatch



custom = APIRouter(prefix="/customers")


database_models.Base.metadata.create_all(bind=engine)




@custom.get("/")
def all_customers():
    with Session(engine) as session:
        stmt = select(database_models.Customer)
        data = session.scalars(stmt).all()
    return data

@custom.get("/{name}")
def get_customer_product_list(name: str):
     with Session(engine) as session:
         stmt = select(database_models.Customer).where( or_
             (database_models.Customer.firstname == name,
             database_models.Customer.lastname == name)
         )
         client = session.scalars(stmt).first()

         if not client:
             raise HTTPException(status_code=404, detail=f"No existing name {name}")

         customer = client
         produits = client.products
         # stmt = select(database_models.Product).where(database_models.Product.owner_id == client.id)
         # liste = session.scalars(stmt).all()



     return {"customer": customer, "products": produits}


@custom.get("/v2/{name}")
def get_customer_product_list(name: str):
    with Session(engine) as session:
        stmt = (
            select(database_models.Customer)
            .options(joinedload(database_models.Customer.products))
            .where(
                or_(
                    database_models.Customer.firstname == name,
                    database_models.Customer.lastname == name
                )
            )
        )

        result = session.scalars(stmt).first()

    return result


@custom.post("/")
def create_customer(customer: CustomerCreate):
    with Session(engine) as session:

        session.add(database_models.Customer(**customer.model_dump()))
        session.commit()
    return {"data":"OK"}

@custom.put("/{id}")
def modify_customers(id: int, customer: CustomerCreate):
   with Session(engine) as session:

        stmt = select(database_models.Customer).where(database_models.Customer.id == id)
        data = session.scalars(stmt).first()
        if not data:
            raise HTTPException(status_code=404, detail="Customer {id} not found")

        for key, value in customer.model_dump().items():
            setattr(data, key, value)

        session.commit()
        session.refresh(data)

   return data

@custom.patch("/{id}")
def patch_customer(id:int, customer: CustomerPatch):
    with Session(engine) as session:
        stmt = select(database_models.Customer).where(database_models.Customer.id == id)
        data = session.scalars(stmt).first()

        if not data:
            raise HTTPException(status_code=404, detail="Product not found")

        for key, value in customer.model_dump(exclude_unset=True).items():
            setattr(data, key, value)
        #if key in allowed_fields:
            # allowed_fields = {"name", "price", "quantity"}
            #
            # for key, value in product.model_dump(exclude_unset=True).items():
            #     if key in allowed_fields:
            #         setattr(data, key, value)

        session.commit()
        session.refresh(data)

        return data


@custom.delete("/{id}")
def delete_customers(id:int):
    with Session(engine) as session:
        stmt = select(database_models.Customer).where(database_models.Customer.id == id)
        data = session.scalars(stmt).first()

        if not data:
            raise HTTPException(status_code=404, detail="Product not found")

        session.delete(data)
        session.commit()

