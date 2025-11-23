from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import bcrypt

from database import SessionLocal, engine
from models import Base, User, Product
import crud
import schemas  # Importamos los esquemas   

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
    User = db.query(User).filter(User.Username == data.Username).first()
    if not User or not bcrypt.checkpw(data.Password.encode("utf-8"), User.Password.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    return {"username": User.Username}

@app.post("/api/register")
def register(data: schemas.RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.Username == data.Username).first()
    if existing:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    hashed_Password = bcrypt.hashpw(data.Password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    new_User = User(Username=data.Username, Password=hashed_Password)

    db.add(new_User)
    db.commit()
    db.refresh(new_User)

    return schemas.UserSchema.from_orm(new_User)

@app.get("/api/productos", response_model=list[schemas.ProductoSchema])
def obtener_productos(db: Session = Depends(get_db)):
    return crud.obtener_productos(db)

@app.get("/api/productos/categoria/{categoria}", response_model=list[schemas.ProductoSchema])
def obtener_productos_por_categoria(categoria: str, db: Session = Depends(get_db)):
    return crud.obtener_productos_por_categoria(db, categoria)

@app.post("/api/productos", response_model=schemas.ProductoSchema)
def crear_product(product: schemas.ProductoSchema, db: Session = Depends(get_db)):
    return crud.crear_product(db, product)