from sqlalchemy.orm import Session
from sqlalchemy import cast, String
from models import Product, Cart, CartItem, Users
from schemas import ProductoCreate, ProductoUpdate
from fastapi import HTTPException

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