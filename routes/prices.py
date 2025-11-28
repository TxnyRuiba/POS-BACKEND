from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Product
from schemas import (
    PrecioUpdate, PrecioBulkRequest, ProductoPrecioSchema, PriceHistorySchema
)
from crud import actualizar_precio, actualizar_precios_en_lote, obtener_historial_precios

router = APIRouter(prefix="/api/precios", tags=["Precios"])

# Listar productos con precio (para pantalla)
@router.get("", response_model=list[ProductoPrecioSchema])
def listar_precios(db: Session = Depends(get_db)):
    productos = (
        db.query(Product)
        .filter(Product.Activo == 1)
        .order_by(Product.Product.asc())
        .all()
    )
    return productos

# Obtener precio de un producto
@router.get("/{product_id}", response_model=ProductoPrecioSchema)
def obtener_precio(product_id: int, db: Session = Depends(get_db)):
    producto = db.query(Product).filter(Product.Id == product_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return producto

# Actualizar precio individual
@router.patch("/{product_id}", response_model=ProductoPrecioSchema)
def cambiar_precio(product_id: int, data: PrecioUpdate, db: Session = Depends(get_db)):
    payload = data.model_dump(by_alias=True)
    new_price = float(payload["Price"])
    reason = payload.get("Reason")
    producto, error = actualizar_precio(db, product_id, new_price, reason)
    if error:
        raise HTTPException(status_code=400, detail=error)
    return producto

# Actualizar precios en lote
@router.post("/lote")
def cambiar_precios_lote(req: PrecioBulkRequest, db: Session = Depends(get_db)):
    items = [i.model_dump(by_alias=True) for i in req.Items]
    resultados = actualizar_precios_en_lote(db, items)
    return {"Resultados": resultados}

# Historial de precios
@router.get("/{product_id}/historial", response_model=list[PriceHistorySchema])
def historial_precios(product_id: int, limit: int = 50, db: Session = Depends(get_db)):
    historial = obtener_historial_precios(db, product_id, limit)
    return historial