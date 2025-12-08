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
from routes.prices import router as price_router

# Crear tablas si no existen
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API POS",
    description="Sistema de Punto de Venta con autenticación JWT",
    version="2.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # ✅ Especifica tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(usuarios_router)
app.include_router(inventory_router)
app.include_router(carritos_router)
app.include_router(price_router)

@app.get("/")
def read_root():
    return {
        "message": "API POS v2.0 - Sistema con autenticación JWT",
        "docs": "/docs",
        "health": "OK"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected"}