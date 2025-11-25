from sqlalchemy.orm import Session
from models import Product
from models import Users
from schemas import ProductoSchema
from models import Cart, CartItem, Product
from sqlalchemy import cast, String

def get_user_by_Username(db: Session, Username: str):
    return db.query(Users).filter(Users.Username == Username).first()

def create_user(db: Session,Username: str, Password: str):
    new_user = Users(Username=Username, Password=Password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def obtener_productos(db: Session):
    return db.query(Product).all()

def obtener_productos_por_categoria(db: Session, category: str):
    return db.query(Product).filter(Product.Category == category).all()

# Obtener todos los productos
def obtener_productos(db: Session):
    return db.query(Product).all()

# Buscar por nombre, código rápido o código de barras
def buscar_productos(db: Session, query: str):
    return db.query(Product).filter(
        (Product.Product.ilike(f"%{query}%")) |
        (Product.Code.ilike(f"%{query}%")) |
        (Product.Barcode.ilike(f"%{query}%"))
    ).all()

# Crear nuevo producto
def crear_product(db: Session, producto: ProductoSchema):
    nuevo = Product(**producto.model_dump())
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

# Actualizar stock
def actualizar_stock(db: Session, id: int, nuevo_stock: int):
    producto = db.query(Product).filter(Product.Id == id).first()
    if not producto:
        return None
    producto.Stock = nuevo_stock
    db.commit()
    db.refresh(producto)
    return producto

# Eliminar producto
def eliminar_producto(db: Session, id: int):
    producto = db.query(Product).filter(Product.Id == id).first()
    if not producto:
        return None
    db.delete(producto)
    db.commit()
    return producto

# Resumen de inventario
def resumen_inventario(db: Session):
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

def crear_carrito(db: Session) -> Cart: #inicia Venta
    cart = Cart()
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return cart

def obtener_carrito(db: Session, cart_id: int) -> Cart | None: #Ver el estado actual del carrito
    return db.query(Cart).filter(Cart.id == cart_id).first()

def buscar_producto(db: Session, product_id=None, code=None, barcode=None) -> Product | None: #Localizar producto o articulo seleccionado
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