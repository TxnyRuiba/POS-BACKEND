import bcrypt
import schemas
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session 
from database import SessionLocal, engine
from models import Base, Users, Product
from sqlalchemy import cast, String
from routes.inventory import router as inventory_router
from routes.users import router as usuarios_router
from routes.cart import router as carritos_router
from routes.inventory import router as inventario_router


# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(inventory_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------ Endpoints ------------------
@app.get("/")
def read_root():
    return {"message": "API funcionando correctamente"}

app.include_router(usuarios_router)
app.include_router(carritos_router)
app.include_router(inventario_router)
