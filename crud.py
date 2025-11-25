from sqlalchemy.orm import Session
from models import Product
from models import Users
from schemas import ProductoSchema

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