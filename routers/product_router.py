from fastapi import APIRouter
from fastapi import HTTPException
from sqlalchemy.orm import Session

from database.database import engine
from sqlalchemy import select

from models import database_models
from schemas.models import ProductCreate, ProductPatch



router = APIRouter(prefix="/products")


database_models.Base.metadata.create_all(bind=engine)





# @router.get("/")
# async def root():
#     return {"message": "Hello World"}

# products = [
#     ProductRead(id = 1, price = 9000, name = "Ballon de Basket",description = "Un ballon de basket de Crazy_Court signé par LeBron James", quantity = 20),
#     ProductRead(id = 2, price = 4300, name = "Salade paradis", description = "Le repas ultime", quantity = 50),
#     ProductRead(id = 3, price = 150000, name = "Portable", description = "Iphone XSMas", quantity = 12),
# ]


# @router.get("/")
# async def say_hello():
#     return {"message": f"Hello Anlim RADJI"}

# @app.get(f"/products")
#
# def all_products():
#     db = session()
#     db.query()
#     return products

@router.get("/first_5_id")
def get_product_by_first_5_id():
    with Session(engine) as session:
        stmt = select(database_models.Product.price).offset(5).limit(10).order_by(database_models.Product.price)
        data = session.scalars(stmt).all()


    return data


@router.get("/mediane")
def get_product_by_first_5_id():
    with Session(engine) as session:
        stmt = select(database_models.Product.price).offset(5).limit(10).order_by(database_models.Product.price)
        data = session.scalars(stmt).all()

        mediane = (data[4] + data[5])/2
    return mediane


@router.get("/")
def all_products():
    with Session(engine) as session:
        stmt = select(database_models.Product)
        data = session.scalars(stmt).all()
    return data

@router.get("/{id}")
def get_product(name: str):
    with Session(engine) as session:
        stmt = select(database_models.Product).where(database_models.Product.name == name)
        data = session.scalars(stmt).first()
    return data




@router.post("/")
def create_products(product: ProductCreate):
    with Session(engine) as session:

        session.add(database_models.Product(**product.model_dump()))
        session.commit()
    return {"data":"OK"}

@router.put("/{id}")
def modify_products(id: int, product: ProductCreate):
   with Session(engine) as session:

        stmt = select(database_models.Product).where(database_models.Product.id == id)
        data = session.scalars(stmt).first()
        if not data:
            raise HTTPException(status_code=404, detail="Product not found")

        for key, value in product.model_dump().items():
            setattr(data, key, value)

        session.commit()
        session.refresh(data)

   return data

@router.patch("/{id}")
def patch_product(id:int, product: ProductPatch):
    with Session(engine) as session:
        stmt = select(database_models.Product).where(database_models.Product.id == id)
        data = session.scalars(stmt).first()

        if not data:
            raise HTTPException(status_code=404, detail="Product not found")

        for key, value in product.model_dump(exclude_unset=True).items():
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


@router.delete("/{id}")
def delete_products(id:int):
    with Session(engine) as session:
        stmt = select(database_models.Product).where(database_models.Product.id == id)
        data = session.scalars(stmt).first()

        if not data:
            raise HTTPException(status_code=404, detail="Product not found")

        session.delete(data)
        session.commit()





# @app.get(f"/product")
# def get_by_id(id:int):
#     for product in products:
#         if product.id == id:
#             return product
#
#     return "product not found"

# @app.post(f"/product")
# def add_product(product:ProductRead):
#     products.append(product)
#     return product
#
# @app.put(f"/product")
# def update_product(id: int, product: ProductRead):
#     for i in range(len(products)):
#         if products[i].id == id:
#             products[i] = product
#
#         return "Modification réussie"
#     return "No products found"

# @app.delete(f"/product")
# def delete_product(id:int):
#     for i in range(len(products)):
#         if products[i].id == id:
#             del products[i]
#
#         return "Produit supprimé"
#     return "No products found"