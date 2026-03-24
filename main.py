from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from routers.product_router import router
from routers.customer_router import custom
from routers.authentification import secu
from fastapi.templating import Jinja2Templates

from database.database import engine
from sqlalchemy import select
from models import database_models

app = FastAPI()

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


app.include_router(router)
app.include_router(custom)
app.include_router(secu)


templates = Jinja2Templates(directory = "templates")
@app.get("/index")
def index(request: Request):
    with Session(engine) as session:
        stmt = select(database_models.Product)
        result = session.scalars(stmt).all()

    return templates.TemplateResponse(request, name = "index.html", context={"request": request,"data": result})
