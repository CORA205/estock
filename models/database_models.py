from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):

    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    role_id = Column(Integer, ForeignKey("Roles.id"))

    customers = relationship("Customer", back_populates="manager")





class Role(Base):
    __tablename__ = "Roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)


class Product(Base):

    __tablename__ = "Products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)
    description = Column(String)
    quantity = Column(Integer)



class Customer(Base):

    __tablename__ = "Customers"

    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String)
    lastname = Column(String)
    manager_id = Column(Integer, ForeignKey("Users.id"))

    manager = relationship(
        "User",
        back_populates="customers"
    )

    orders = relationship("Order", back_populates="customer")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("Customers.id"))

    items = relationship("OrderItem", back_populates="order", cascade="all, delete")

    customer = relationship("Customer", back_populates="orders")



class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True)

    order_id = Column(Integer, ForeignKey("orders.id"))
    product_id = Column(Integer, ForeignKey("Products.id"))

    quantity = Column(Integer)
    price = Column(Float)

    order = relationship("Order", back_populates="items")