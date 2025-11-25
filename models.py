from sqlalchemy import Column, Integer, String, Float
from database import Base

class Users(Base):
    __tablename__ = "Users"

    ID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Username = Column(String, unique=True, index=True, nullable=False)
    Password = Column(String, nullable=False)


class Product(Base):
    __tablename__ = "Master_Data"

    Id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Code = Column(String, unique=True, index=True, nullable=False)
    Barcode = Column(String, unique=True, index=True, nullable=False)
    Product = Column(String, nullable=False)
    Category = Column(String, nullable=False)
    Units = Column(String, nullable=False)
    Price = Column(Float, nullable=False)
    Stock = Column(Integer, nullable=False)
    Min_Stock = Column(Integer, nullable=False)
