from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import cast, String
from database import get_db
from models import Product
from schemas import (
    ProductoSchema,
    ProductoCreate,
    ProductoUpdate,
)
from crud import eliminar_producto as crud_eliminar_producto

router = APIRouter(prefix="/api/inventario", tags=["Inventario"])

# Listar todos los productos
@router.get("", response_model=list[ProductoSchema])
def obtener_inventario(db: Session = Depends(get_db)):
    return db.query(Product).all()

# Buscar productos por nombre, código o código de barras
@router.get("/buscar", response_model=list[ProductoSchema])
def buscar_productos(query: str, db: Session = Depends(get_db)):
    return db.query(Product).filter(
        (Product.Product.ilike(f"%{query}%")) |
        (cast(Product.Code, String).ilike(f"%{query}%")) |
        (cast(Product.Barcode, String).ilike(f"%{query}%"))
    ).all()

# Crear nuevo producto
@router.post("", response_model=ProductoSchema, status_code=201)
def crear_producto(producto: ProductoCreate, db: Session = Depends(get_db)):
    nuevo = Product(**producto.model_dump(by_alias=True))
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

# Eliminar producto
@router.delete("/{id}")
def eliminar_producto(id: int, db: Session = Depends(get_db)):
    producto = crud_eliminar_producto(db, id)  # usa la lógica de inactivar
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"mensaje": "Producto marcado como inactivo"}

# Resumen de inventario
@router.get("/resumen")
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

# Actualización integral de producto
@router.patch("/{product_id}", response_model=ProductoSchema)
def actualizar_producto(product_id: int, data: ProductoUpdate, db: Session = Depends(get_db)):
    producto = db.query(Product).filter(Product.Id == product_id).first()
    if not producto:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    for field, value in data.model_dump(exclude_unset=True, by_alias=True).items():
        setattr(producto, field, value)

    db.commit()
    db.refresh(producto)
    return producto