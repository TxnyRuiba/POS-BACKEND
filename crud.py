from sqlalchemy.orm import Session
from sqlalchemy import cast, String
from models import Product, Cart, CartItem, Users, PriceHistory
from schemas import ProductoCreate, ProductoUpdate
from fastapi import HTTPException
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

# ------------------ Usuarios ------------------
def get_user_by_username(db: Session, username: str) -> Users | None:
    return db.query(Users).filter(Users.Username == username).first()

def create_user(db: Session, username: str, password: str) -> Users:
    new_user = Users(Username=username, Password=password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

# ------------------ Productos ------------------
def obtener_productos(db: Session) -> list[Product]:
    return db.query(Product).all()

def buscar_productos(db: Session, query: str) -> list[Product]:
    return db.query(Product).filter(
        (Product.Product.ilike(f"%{query}%")) |
        (cast(Product.Code, String).ilike(f"%{query}%")) |
        (cast(Product.Barcode, String).ilike(f"%{query}%"))
    ).all()

def crear_producto(db: Session, producto: ProductoCreate) -> Product:
    nuevo = Product(**producto.model_dump(by_alias=True))
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

def actualizar_stock(db: Session, id: int, nuevo_stock: int) -> Product | None:
    producto = db.query(Product).filter(Product.Id == id).first()
    if not producto:
        return None
    producto.Stock = nuevo_stock
    db.commit()
    db.refresh(producto)
    return producto

def eliminar_producto(db: Session, id: int):
    producto = db.query(Product).filter(Product.Id == id).first()
    if not producto:
        return None
    producto.Activo = 0
    db.commit()
    return producto

def resumen_inventario(db: Session) -> dict:
    total = db.query(Product).count()
    bajo = db.query(Product).filter(Product.Stock <= Product.Min_Stock).count()
    normal = total - bajo
    categorias = db.query(Product.Category).distinct().count()
    return {
        "TotalProductos": total,
        "StockBajo": bajo,
        "StockNormal": normal,
        "Categorias": categorias
    }

def actualizar_producto(db: Session, product_id: int, data: ProductoUpdate) -> Product | None:
    producto = db.query(Product).filter(Product.Id == product_id).first()
    if not producto:
        return None
    for field, value in data.model_dump(exclude_unset=True, by_alias=False).items():
        setattr(producto, field, value)
    db.commit()
    db.refresh(producto)
    return producto

# ------------------ Carritos ------------------
def crear_carrito(db: Session) -> Cart:
    cart = Cart()
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return cart

def obtener_carrito(db: Session, cart_id: int) -> Cart | None:
    return db.query(Cart).filter(Cart.id == cart_id).first()

def buscar_producto(db: Session, product_id=None, code=None, barcode=None) -> Product | None:
    q = db.query(Product)
    if product_id:
        return q.filter(Product.Id == product_id).first()
    if code:
        return q.filter(cast(Product.Code, String).ilike(f"%{code}%")).first()
    if barcode:
        return q.filter(cast(Product.Barcode, String).ilike(f"%{barcode}%")).first()
    return None

def agregar_item(db: Session, cart_id: int, product: Product, quantity: float) -> CartItem:
    subtotal = float(product.Price) * float(quantity)
    item = CartItem(
        cart_id=cart_id,
        product_id=product.Id,
        product_name=product.Product,
        price=float(product.Price),
        quantity=float(quantity),
        subtotal=subtotal,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

def actualizar_item(db: Session, item_id: int, quantity: float) -> CartItem | None:
    item = db.query(CartItem).filter(CartItem.id == item_id).first()
    if not item:
        return None
    item.quantity = float(quantity)
    item.subtotal = float(item.price) * float(item.quantity)
    db.commit()
    db.refresh(item)
    return item

def resumen_carrito(db: Session, cart_id: int) -> dict | None:
    cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if not cart:
        return None
    total = sum(i.subtotal for i in cart.items)
    return {"cart": cart, "total": float(total)}

def eliminar_item_carrito(db: Session, cart_id: int, item_id: int):
    item = db.query(CartItem).filter(CartItem.cart_id == cart_id, CartItem.id == item_id).first()
    if not item:
        return None, "Item no encontrado"
    db.delete(item)
    db.commit()
    return True, None

def vaciar_carrito(db: Session, cart_id: int):
    items = db.query(CartItem).filter(CartItem.cart_id == cart_id).all()
    for item in items:
        db.delete(item)
    db.commit()
    return True

def cambiar_estado_carrito(db: Session, cart_id: int, new_status: str):
    cart = db.query(Cart).filter(Cart.id == cart_id).first()
    if not cart:
        return None, "Carrito no encontrado"
    cart.status = new_status
    db.commit()
    db.refresh(cart)
    return cart, None

def actualizar_cantidad_item(db: Session, cart_id: int, item_id: int, new_qty: int):
    item = db.query(CartItem).filter(CartItem.cart_id == cart_id, CartItem.id == item_id).first()
    if not item:
        return None, "Item no encontrado"
    if new_qty <= 0:
        return None, "Cantidad inválida"
    item.quantity = new_qty
    db.commit()
    db.refresh(item)
    return item, None

def calcular_total_carrito(db: Session, cart_id: int):
    items = db.query(CartItem).filter(CartItem.cart_id == cart_id).all()
    total = sum(i.price * i.quantity for i in items)
    return total


#Precios
def actualizar_precio(db: Session, product_id: int, new_price: float, reason: str | None = None):
    producto = db.query(Product).filter(Product.Id == product_id).first()
    if not producto:
        return None, "Producto no encontrado"

    if producto.Activo == 0:
        return None, "Producto inactivo"

    if new_price < 0:
        return None, "Precio no puede ser negativo"

    old_price = producto.Price
    if round(old_price, 2) == round(new_price, 2):
        return None, "El nuevo precio es igual al actual"

    producto.Price = float(round(new_price, 2))
    db.add(producto)

    # Registrar historial (opcional pero recomendado)
    hist = PriceHistory(
        Product_Id=producto.Id,
        Old_Price=old_price,
        New_Price=producto.Price,
        Reason=reason,
        Changed_At=datetime.utcnow()
    )
    db.add(hist)

    db.commit()
    db.refresh(producto)
    return producto, None

def actualizar_precios_en_lote(db: Session, items: list[dict]):
    resultados = []
    for item in items:
        pid = int(item["Id"])
        price = float(item["Price"])
        reason = item.get("Reason")
        producto, error = actualizar_precio(db, pid, price, reason)
        resultados.append({
            "Id": pid,
            "Success": error is None,
            "Error": error if error else None,
            "NewPrice": producto.Price if producto else None
        })
    return resultados

def obtener_historial_precios(db: Session, product_id: int, limit: int = 50):
    return (
        db.query(PriceHistory)
        .filter(PriceHistory.product_id == product_id)
        .order_by(PriceHistory.changed_at.desc())
        .limit(limit)
        .all()
    )