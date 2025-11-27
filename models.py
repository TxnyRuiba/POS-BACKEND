from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Float, ForeignKey
from database import Base
from sqlalchemy.orm import relationship

class Users(Base):
    __tablename__ = "Users"

    ID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Username = Column(String, unique=True, index=True, nullable=False)
    Password = Column(String, nullable=False)


class Product(Base):
    __tablename__ = "Master_Data"

    Id = Column(Integer, primary_key = True, index = True, autoincrement = True)
    Code = Column(String, unique = True, index = True, nullable = False)
    Barcode = Column(String, unique = True, index = True, nullable = False)
    Product = Column(String, nullable = False)
    Category = Column(String, nullable = False)
    Units = Column(String, nullable = False)
    Price = Column(Float, nullable = False)
    Stock = Column(Integer, nullable = False)
    Min_Stock = Column(Integer, nullable = False)
    Activo = Column(Integer, default = 1)  # 1 = activo, 0 = inactivo


#Carrito
class Cart(Base):
    __tablename__ = "cart"
    id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String, nullable=False, default="open")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")

class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    cart_id = Column(Integer, ForeignKey("cart.id", ondelete="CASCADE"), nullable=False)
    product_id = Column(Integer, ForeignKey("Master_Data.Id"), nullable=False)
    product_name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False, default=1.0)
    subtotal = Column(Float, nullable=False)
    cart = relationship("Cart", back_populates="items")