from sqlalchemy import Column, Integer, String, Float
from database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)  # autoincrement automático
    username = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)

class Producto(Base):
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    image = Column(String)
    category = Column(String)
    code = Column(String)
    unit = Column(String)
