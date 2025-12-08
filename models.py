from decimal import Decimal
from sqlalchemy import Column, Integer, String, NUMERIC, ForeignKey, BigInteger, Text, Index, DateTime
from datetime import datetime
from database import Base
from sqlalchemy.orm import relationship

class Users(Base):
    __tablename__ = "Users"

    ID = Column(Integer, primary_key=True, index=True, autoincrement=True)
    Username = Column(String, unique=True, index=True, nullable=False)
    Password = Column(String, nullable=False)
    Role = Column(String, default="cashier")  # NUEVO: admin, manager, cashier


class Product(Base):
    __tablename__ = "Master_Data"

    Id = Column(Integer, primary_key = True, index = True, autoincrement = True)
    Code = Column(String, unique = True, index = True, nullable = False)
    Barcode = Column(String, unique = True, index = True, nullable = False)
    Product = Column(String, nullable = False)
    Category = Column(String, nullable = False)
    Units = Column(String, nullable = False)
    Price = Column(NUMERIC(10, 2), nullable=False)
    Stock = Column(Integer, nullable = False)
    Min_Stock = Column(Integer, nullable = False)
    Activo = Column(Integer, default = 1)  # 1 = activo, 0 = inactivo
    __table_args__ = (
        Index('idx_product_active', 'Activo'),
        Index('idx_product_category_active', 'Category', 'Activo'),\
    )

#Carrito
class Cart(Base):
    __tablename__ = "cart"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("Users.ID"), nullable=True)  # NUEVO
    status = Column(Text, default="open")  # open, completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)  # NUEVO
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(BigInteger, primary_key=True, index=True)
    cart_id = Column(BigInteger, ForeignKey("cart.id"), nullable=False)
    product_id = Column(BigInteger, ForeignKey("Master_Data.Id"), nullable=False)
    product_name = Column(Text, nullable=False)
    price = Column(NUMERIC(10, 2), nullable=False)  # CAMBIADO
    quantity = Column(NUMERIC(10, 3), nullable=False)  # CAMBIADO: permite 0.5kg, etc
    subtotal = Column(NUMERIC(10, 2), nullable=False)  # CAMBIADO
    cart = relationship("Cart", back_populates="items")
  

class PriceHistory(Base):
    __tablename__ = "price_history"

    id = Column(BigInteger, primary_key=True, index=True)
    product_id = Column(BigInteger, ForeignKey("Master_Data.Id"), nullable=False, index=True)
    old_price = Column(NUMERIC(10, 2), nullable=False)  # CAMBIADO
    new_price = Column(NUMERIC(10, 2), nullable=False)  # CAMBIADO
    reason = Column(Text, nullable=True)
    changed_at = Column(DateTime, default=datetime.utcnow)

    product = relationship("Product")

    # NUEVO: Modelo de Ticket de Venta
class SaleTicket(Base):
    __tablename__ = "sale_tickets"
    
    id = Column(BigInteger, primary_key=True, index=True)
    ticket_number = Column(String, unique=True, nullable=False, index=True)  # TKT-20231207-001
    cart_id = Column(BigInteger, ForeignKey("cart.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("Users.ID"), nullable=False)  # Cajero
    
    subtotal = Column(NUMERIC(10, 2), nullable=False)
    tax = Column(NUMERIC(10, 2), default=Decimal('0.00'))
    discount = Column(NUMERIC(10, 2), default=Decimal('0.00'))
    total = Column(NUMERIC(10, 2), nullable=False)
    
    payment_method = Column(String, nullable=False)  # cash, card, transfer
    payment_reference = Column(String, nullable=True)  # Para tarjeta/transferencia
    
    status = Column(String, default="completed")  # completed, cancelled
    created_at = Column(DateTime, default=datetime.utcnow)
    cancelled_at = Column(DateTime, nullable=True)
    cancelled_by = Column(Integer, ForeignKey("Users.ID"), nullable=True)
    cancellation_reason = Column(Text, nullable=True)

    # Relaciones
    cart = relationship("Cart")
    cashier = relationship("Users", foreign_keys=[user_id])
    cancelled_by_user = relationship("Users", foreign_keys=[cancelled_by])
    items = relationship("SaleTicketItem", back_populates="ticket", cascade="all, delete-orphan")
    
    # NUEVO: Items del ticket (snapshot de la venta)
class SaleTicketItem(Base):
    __tablename__ = "sale_ticket_items"
    
    id = Column(BigInteger, primary_key=True, index=True)
    ticket_id = Column(BigInteger, ForeignKey("sale_tickets.id"), nullable=False)
    product_id = Column(BigInteger, nullable=False)  # No FK para mantener histórico
    product_code = Column(String, nullable=False)
    product_name = Column(Text, nullable=False)
    unit_price = Column(NUMERIC(10, 2), nullable=False)
    quantity = Column(NUMERIC(10, 3), nullable=False)
    subtotal = Column(NUMERIC(10, 2), nullable=False)
    
    ticket = relationship("SaleTicket", back_populates="items")


# NUEVO: Control de Caja
class CashRegister(Base):
    __tablename__ = "cash_register"
    
    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("Users.ID"), nullable=False)
    opened_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    
    initial_cash = Column(NUMERIC(10, 2), default=Decimal('0.00'))
    final_cash = Column(NUMERIC(10, 2), nullable=True)
    
    total_sales = Column(NUMERIC(10, 2), default=Decimal('0.00'))
    total_cash = Column(NUMERIC(10, 2), default=Decimal('0.00'))
    total_card = Column(NUMERIC(10, 2), default=Decimal('0.00'))
    
    status = Column(String, default="open")  # open, closed
    notes = Column(Text, nullable=True)
    
    user = relationship("Users")
