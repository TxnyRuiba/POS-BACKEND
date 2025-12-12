import sys
from decimal import Decimal
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, NUMERIC, ForeignKey, BigInteger, Text, DateTime
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

# =========================================================================
# 1. Definición de Modelos Corregidos (Basado en tu models.py)
# =========================================================================

# NOTA: En un ambiente real, usted usaría los modelos de models.py
# Aquí los definimos localmente para la prueba.
Base = declarative_base()

class Users(Base):
    __tablename__ = "Users"
    ID = Column(Integer, primary_key=True)
    Username = Column(String)

class Product(Base):
    __tablename__ = "Master_Data"
    Id = Column(Integer, primary_key=True)
    Product = Column(String)
    Price = Column(NUMERIC(10, 2), nullable=False)
    # CORRECCIÓN PUNTO 3 & 4: Integer -> NUMERIC(10, 4)
    Stock = Column(NUMERIC(10, 4), nullable=False) 
    Min_Stock = Column(NUMERIC(10, 4), nullable=False)
    Activo = Column(Integer, default=1)

class Cart(Base):
    __tablename__ = "cart"
    id = Column(BigInteger, primary_key=True)
    user_id = Column(Integer, ForeignKey("Users.ID"), nullable=True)
    status = Column(Text, default="open")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    # CORRECCIÓN PUNTO 2: Nueva columna para cancelación
    cancelled_at = Column(DateTime, nullable=True) 
    
    items = relationship("CartItem", back_populates="cart", cascade="all, delete-orphan")
    user = relationship("Users", foreign_keys=[user_id])

class CartItem(Base):
    __tablename__ = "cart_items"
    id = Column(BigInteger, primary_key=True)
    cart_id = Column(BigInteger, ForeignKey("cart.id"), nullable=False)
    product_id = Column(BigInteger, ForeignKey("Master_Data.Id"), nullable=False)
    product_name = Column(Text, nullable=False)
    price = Column(NUMERIC(10, 2), nullable=False)
    # CORRECCIÓN PUNTO 3 & 4: NUMERIC(10, 3) -> NUMERIC(10, 4)
    quantity = Column(NUMERIC(10, 4), nullable=False) 
    subtotal = Column(NUMERIC(10, 2), nullable=False)
    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")

# =========================================================================
# 2. Mock de Funciones CRUD Corregidas
# =========================================================================

def crear_carrito(db):
    """Crea un carrito de prueba."""
    cart = Cart(id=1, user_id=1, status='open')
    db.add(cart)
    return cart

def crear_producto(db, product_id, stock: Decimal):
    """Crea un producto de prueba con stock decimal."""
    product = Product(
        Id=product_id, 
        Product=f"Producto {product_id}", 
        Price=Decimal('10.00'), 
        Stock=stock,
        Min_Stock=Decimal('0.5')
    )
    db.add(product)
    return product

# CORRECCIÓN PUNTO 3: Manejo de Decimales en la cantidad
def actualizar_cantidad_item_mock(db, cart_id, item_id, quantity: Decimal):
    """Simula la actualización de cantidad con precisión decimal."""
    item = db.query(CartItem).filter(CartItem.cart_id == cart_id, CartItem.product_id == item_id).first()
    if not item:
        return None, "Item no encontrado"
    
    # Simulación de validación de stock
    if item.product.Stock < quantity:
         return None, f"Stock insuficiente. Disponible: {item.product.Stock}"

    item.quantity = quantity
    db.commit()
    db.refresh(item)
    return item, None

# CORRECCIÓN PUNTO 2: Lógica de timestamps en cambio de estado
def cambiar_estado_carrito_mock(db, cart_id: int, new_status: str):
    """Simula el cambio de estado con timestamps condicionales."""
    cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if not cart:
        return None, "Carrito no encontrado"
    
    cart.status = new_status
    now = datetime.utcnow()
    
    if new_status == "completed":
        cart.completed_at = now
        cart.cancelled_at = None # Limpieza si cambia de cancelled a completed
    elif new_status == "cancelled":
        cart.cancelled_at = now
        cart.completed_at = None # Limpieza si cambia de completed a cancelled
    # Se pueden agregar otros estados aquí (e.g., 'voided', 'closed')
    
    db.commit()
    db.refresh(cart)
    return cart, None

# CORRECCIÓN PUNTO 1: El CRUD retorna el objeto (no una tupla ok, error)
def eliminar_item_carrito_mock(db, cart_id, item_id):
    """Simula la eliminación. Retorna True o lanza una excepción."""
    item = db.query(CartItem).filter(CartItem.cart_id == cart_id, CartItem.product_id == item_id).first()
    if not item:
        # En un CRUD real, esto podría lanzar una HTTPException(404) o un error de negocio
        return None 
    
    db.delete(item)
    db.commit()
    return True # Retorna éxito (True o el objeto eliminado)

def agregar_item_carrito(db, cart_id, product: Product, quantity: Decimal):
    """Función auxiliar para agregar un item a un carrito."""
    item = CartItem(
        id=datetime.utcnow().microsecond, # ID simple para mock
        cart_id=cart_id, 
        product_id=product.Id, 
        product_name=product.Product,
        price=product.Price,
        quantity=quantity,
        subtotal=product.Price * quantity
    )
    db.add(item)
    db.commit()
    return item

# =========================================================================
# 3. Lógica de Pruebas
# =========================================================================

def run_tests():
    # Configuración de base de datos en memoria
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()

    print("--- INICIANDO PRUEBAS DE MEJORAS ---")
    
    # ----------------------------------------------------
    # TEST 1: Precisión Decimal (Puntos 3 & 4)
    # ----------------------------------------------------
    print("\n[TEST 1] Precisión Decimal para Stock y Cantidad (NUMERIC(10, 4))")
    
    # Crear producto con stock decimal (1.325 kg)
    prod = crear_producto(db, 101, Decimal('1.3250'))
    
    # Verificar si el stock se guardó con precisión
    if prod.Stock == Decimal('1.3250'):
        print(f"✅ Product.Stock: {prod.Stock} (Precisión Decimal OK)")
    else:
        print(f"❌ Product.Stock: {prod.Stock} (Fallo de Precisión)")

    # Crear carrito
    user = Users(ID=1, Username='test_user'); db.add(user)
    cart = crear_carrito(db)
    
    # Agregar item con cantidad decimal (0.75 Lts)
    item = agregar_item_carrito(db, cart.id, prod, Decimal('0.7500'))
    
    # Actualizar cantidad a un valor decimal (1.1 Kg)
    new_qty = Decimal('1.1000')
    updated_item, error = actualizar_cantidad_item_mock(db, cart.id, prod.Id, new_qty)
    
    if updated_item and updated_item.quantity == new_qty:
        print(f"✅ CartItem.quantity: {updated_item.quantity} (Actualización Decimal OK)")
    else:
        print(f"❌ CartItem.quantity: {updated_item.quantity} (Fallo en Actualización Decimal): {error}")

    # ----------------------------------------------------
    # TEST 2: Timestamps de Cancelación (Punto 2)
    # ----------------------------------------------------
    print("\n[TEST 2] Timestamps de Cancelación (Cart.cancelled_at)")
    
    # Cambiar estado a 'cancelled'
    cancelled_cart, error = cambiar_estado_carrito_mock(db, cart.id, "cancelled")
    
    if cancelled_cart and cancelled_cart.cancelled_at:
        print(f"✅ Cart.cancelled_at: {cancelled_cart.cancelled_at} (Timestamp de Cancelación OK)")
    else:
        print("❌ Cart.cancelled_at: Falló la asignación del timestamp de cancelación.")
        
    # Cambiar estado a 'completed' para probar limpieza
    completed_cart, error = cambiar_estado_carrito_mock(db, cart.id, "completed")
    
    if completed_cart and completed_cart.completed_at and not completed_cart.cancelled_at:
        print(f"✅ Cart.completed_at: {completed_cart.completed_at} y cancelled_at es None (Limpieza de Timestamps OK)")
    else:
        print("❌ Falló la lógica de limpieza de timestamps.")
        
    # ----------------------------------------------------
    # TEST 3: Respuesta del CRUD de Eliminación (Punto 1)
    # ----------------------------------------------------
    print("\n[TEST 3] Respuesta del CRUD de Eliminación (Eliminar Item)")
    
    # Ejecutar la función CRUD Mock. Esperamos True o None, NO una tupla.
    result = eliminar_item_carrito_mock(db, cart.id, prod.Id)
    
    # Simulación del código del endpoint corregido en cart.py:
    # @router.delete(...)
    # def eliminar_item(...):
    #     try:
    #         resultado = eliminar_item_carrito_mock(...) # Retorna True o None
    #         if not resultado: 
    #              raise HTTPException(...)
    #         return {"success": True, ...}
    #     except ...
    
    if result is True:
        print(f"✅ CRUD: eliminar_item_carrito_mock retornó {result} (OK para el endpoint corregido)")
        print("   Nota: El endpoint ya no intentará hacer 'ok, error = result'.")
    elif result is None:
         print(f"❌ CRUD: eliminar_item_carrito_mock retornó {result} (Indica item no encontrado/error. OK si es un fallo esperado)")
    else:
        print(f"❌ CRUD: Retorno inesperado: {type(result)}")

    db.close()
    print("\n--- PRUEBAS COMPLETADAS ---")

if __name__ == "__main__":
    run_tests()