from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str
    role_id: int | None = None

class UserLogin(BaseModel):
    username: str
    password: str



class ProductRead(BaseModel):
    id: int
    name: str
    price: float
    description: str
    quantity: int



class ProductCreate(BaseModel):
    name: str
    price: float
    description: str
    quantity: int


class ProductPatch(BaseModel):
    name: str | None = None
    price: float | None = None
    description: str | None = None
    quantity: int | None = None



class CustomerRead(BaseModel):
    id: int
    firstname: str
    lastname: str
    manager_id: int


class CustomerCreate(BaseModel):
    firstname: str
    lastname: str
    manager_id: int


class CustomerPatch(BaseModel):
    firstname: str | None = None
    lastname: str | None = None
    manager_id: int | None = None


class OrderRead(BaseModel):
    id : int
    customer_id : int

class OrderCreate(BaseModel):
    customer_id : int


class OrderItemRead(BaseModel):
    id : int
    order_id : int
    product_id : int
    quantity : int
    price : float

class OrderItemCreate(BaseModel):
    order_id : int
    product_id : int
    quantity : int
    price : float

class RoleCreate(BaseModel):
    name: str

class RoleRead(BaseModel):
    id: int
    name: str