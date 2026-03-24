from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str


class ProductRead(BaseModel):
    id: int
    name: str
    price: float
    description: str
    quantity: int
    owner_id: int


class ProductCreate(BaseModel):
    name: str
    price: float
    description: str
    quantity: int
    owner_id: int

class ProductPatch(BaseModel):
    name: str | None = None
    price: float | None = None
    description: str | None = None
    quantity: int | None = None
    owner_id: int | None = None


class CustomerRead(BaseModel):
    id: int
    firstname: str
    lastname: str


class CustomerCreate(BaseModel):
    firstname: str
    lastname: str


class CustomerPatch(BaseModel):
    firstname: str | None = None
    lastname: str | None = None
