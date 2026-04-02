from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from utils.init_superadmin import create_superadmin

from routers.product_router import router
from routers.customer_router import custom
from routers.authentification import secu
from routers.order_router import command
from routers.order_item_router import items
from routers.rbac import ropes

from fastapi.templating import Jinja2Templates

from database.database import engine
from sqlalchemy import select
from models import database_models

app = FastAPI(title="Stock")

origins = [
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# main.py — appeler au démarrage

@app.on_event("startup")
def startup():
    create_superadmin()


app.include_router(secu)
app.include_router(ropes)
app.include_router(router)
app.include_router(custom)
app.include_router(command)
app.include_router(items)


templates = Jinja2Templates(directory = "templates")
@app.get("/index")
def index(request: Request):
    with Session(engine) as session:
        stmt = select(database_models.Product)
        result = session.scalars(stmt).all()

    return templates.TemplateResponse(request, name = "index.html", context={"request": request,"data": result})
