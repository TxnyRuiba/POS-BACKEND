from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, Float, ForeignKey, BigInteger, Text
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

    id = Column(BigInteger, primary_key=True, index=True)
    status = Column(Text, default="open")
    created_at = Column(DateTime, default=datetime.utcnow)
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(BigInteger, primary_key=True, index=True)
    cart_id = Column(BigInteger, ForeignKey("cart.id"), nullable=False)
    product_id = Column(BigInteger, ForeignKey("Master_Data.Id"), nullable=False)
    product_name = Column(Text, nullable=False)
    price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=False)
    subtotal = Column(Float, nullable=False)
    cart = relationship("Cart", back_populates="items")
  

class PriceHistory(Base):
    __tablename__ = "Price_History"

    id = Column(BigInteger, primary_key=True, index=True)
    product_id = Column(BigInteger, ForeignKey("Master_Data.Id"), nullable=False, index=True)
    old_price = Column(Float, nullable=False)
    new_price = Column(Float, nullable=False)
    reason = Column(Text, nullable=True)
    changed_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product")