from sqlalchemy import Column, Integer, String, Float
from database import Base

class User(Base):
    __tablename__ = "Users"

    id = Column(Integer, primary_key=True, index=True)  # autoincrement automático
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

class Product(Base):
    __tablename__ = "Master_Data"

    Id = Column(Integer, primary_key=True, index=True)
    Code = Column(Integer, unique=True, index=True)        # antes "Code"
    Barcode = Column(String, nullable=True)                # antes "Barcode"
    Product = Column(String, nullable=False)               # antes "Product"
    Category = Column(String, nullable=True)               # antes "Category"
    Unit = Column(String, nullable=True)                   # antes "Units"
    Price = Column(Float, nullable=False)                  # antes "Price"
    Stock = Column(Float, nullable=False)                  # antes "Stock"
    Min_stock = Column(Integer, nullable=False)            # antes "Min_Stock"
