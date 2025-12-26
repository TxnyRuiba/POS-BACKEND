import schemas
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from database import engine
from models import Base
from fastapi.responses import JSONResponse


# Importar routers
from routes.inventory import router as inventory_router
from routes.users import router as usuarios_router
from routes.cart import router as carritos_router
from routes.prices import router as price_router
from routes.tickets import router as tickets_router
from routes.cash_register import router as cash_register_router
from routes.withdrawals import router as withdrawals_router
from app.core.exceptions import AppException

# Crear tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API POS Sistema Completo",
    description="Sistema de Punto de Venta con autenticación, tickets y caja registradora",
    version="3.0.0"
)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    # y luego el dominio real cuando lo tengan
]

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(usuarios_router)
app.include_router(inventory_router)
app.include_router(carritos_router)
app.include_router(price_router)
app.include_router(tickets_router)
app.include_router(cash_register_router)
app.include_router(withdrawals_router)

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Manejador global para excepciones personalizadas"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.message,
            "type": exc.__class__.__name__,
            "path": str(request.url)
        }
    )

@app.get("/")
def read_root():
    return {
        "message": "API POS v3.0 - Sistema Completo",
        "features": [
            "Autenticación JWT con roles",
            "Gestión de inventario",
            "Carritos de compra",
            "Tickets de venta",
            "Control de caja registradora",
            "Reportes de ventas"
        ],
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "3.0.0"}