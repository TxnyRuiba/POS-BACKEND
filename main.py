import bcrypt
import crud
import schemas  # Importamos los esquemas 
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session 
from database import SessionLocal, engine
from models import Base, Users, Product
from schemas import StockUpdate
from sqlalchemy import cast, String

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ Dependencia DB ------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ------------------ Endpoints ------------------
@app.get("/")
def read_root():
    return {"message": "API funcionando correctamente"}

@app.post("/api/login")
def login(data: schemas.LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.Username == data.username).first()
    if not user or not bcrypt.checkpw(data.password.encode("utf-8"), user.Password.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    return {"username": user.Username}

@app.post("/api/register")
def register(data: schemas.RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(Users).filter(Users.Username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    hashed_password = bcrypt.hashpw(data.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    new_user = Users(Username=data.username, Password=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return schemas.UserSchema.from_orm(new_user)

@app.get("/api/inventario", response_model=list[schemas.ProductoSchema])
def obtener_inventario(db: Session = Depends(get_db)):
    return db.query(Product).all()

@app.get("/api/inventario/buscar", response_model=list[schemas.ProductoSchema])
def buscar_productos(query: str, db: Session = Depends(get_db)):
    return db.query(Product).filter(
        (Product.Product.ilike(f"%{query}%")) |
        (cast(Product.Code, String).ilike(f"%{query}%")) |
        (cast(Product.Barcode, String).ilike(f"%{query}%"))
    ).all()

@app.post("/api/inventario", response_model=schemas.ProductoSchema)
def crear_producto(producto: schemas.ProductoSchema, db: Session = Depends(get_db)):
    nuevo = Product(**producto.model_dump(by_alias=True, exclude={"Id"}))
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

@app.put("/api/inventario/{id}/stock", response_model=schemas.ProductoSchema)
def actualizar_stock(id: int, data: StockUpdate, db: Session = Depends(get_db)):
    producto = crud.actualizar_stock(db, id, data.nuevo_stock)
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return schemas.ProductoSchema.from_orm(producto)

@app.delete("/api/inventario/{id}")
def eliminar_producto(id: int, db: Session = Depends(get_db)):
    producto = db.query(Product).filter(Product.Id == id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    db.delete(producto)
    db.commit()
    return {"mensaje": "Producto eliminado correctamente"}

@app.get("/api/inventario/resumen")
def resumen_inventario(db: Session = Depends(get_db)):
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
#Crear Carrito
@app.post("/api/pos/carritos", response_model=schemas.CartSchema)
def crear_carrito_endpoint(db: Session = Depends(get_db)):
    cart = crud.crear_carrito(db)
    # from_orm para mapear, luego añadimos total
    cart_schema = schemas.CartSchema.from_orm(cart)
    return cart_schema.model_dump() | {"total": 0.0}
#Agregar aruticulo
@app.post("/api/pos/carritos/{cart_id}/items", response_model=schemas.CartItemSchema)
def agregar_item_endpoint(cart_id: int, data: schemas.AddItemRequest, db: Session = Depends(get_db)):
    cart = crud.obtener_carrito(db, cart_id)
    if not cart or cart.status != "open":
        raise HTTPException(status_code=404, detail="Carrito no disponible")

    product = crud.buscar_producto(db, product_id=data.product_id, code=data.code, barcode=data.barcode)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    # Validación de stock (opcional, según negocio)
    if product.Stock is not None and float(product.Stock) < float(data.quantity):
        raise HTTPException(status_code=400, detail="Stock insuficiente")

    item = crud.agregar_item(db, cart_id, product, data.quantity)
    return schemas.CartItemSchema.from_orm(item)
#Total Carrito
@app.get("/api/pos/carritos/{cart_id}", response_model=schemas.CartSchema)
def obtener_carrito_endpoint(cart_id: int, db: Session = Depends(get_db)):
    cart = crud.obtener_carrito(db, cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Carrito no encontrado")
    total = sum(i.subtotal for i in cart.items)
    cart_schema = schemas.CartSchema.from_orm(cart)
    return cart_schema.model_dump() | {"total": total}