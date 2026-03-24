from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):

    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String, nullable=False)

    customers = relationship("Customer", back_populates="manager")


class Product(Base):

    __tablename__ = "Products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    price = Column(Float)
    description = Column(String)
    quantity = Column(Integer)
    owner_id = Column(Integer, ForeignKey("Customers.id"))
    owner = relationship(
        "Customer",
        back_populates="products"
    )


class Customer(Base):

    __tablename__ = "Customers"

    id = Column(Integer, primary_key=True, index=True)
    firstname = Column(String)
    lastname = Column(String)
    manager_id = Column(Integer, ForeignKey("Users.id"))

    products = relationship(
        "Product",
    back_populates = "owner",
    cascade = "all, delete"
    )
    manager = relationship(
        "User",
        back_populates="customers"
    )
