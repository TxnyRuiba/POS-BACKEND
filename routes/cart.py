from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import CartSchema, CartItemSchema, AddItemRequest
from crud import crear_carrito, obtener_carrito, buscar_producto, agregar_item
from models import Product

router = APIRouter(prefix="/api/pos/carts", tags=["Carts"])

@router.post("", response_model=CartSchema)
def crear_carrito_endpoint(db: Session = Depends(get_db)):
    cart = crear_carrito(db)
    cart_schema = CartSchema.from_orm(cart)
    return cart_schema.model_dump() | {"total": 0.0}

@router.post("/{cart_id}/items", response_model=CartItemSchema)
def agregar_item_endpoint(cart_id: int, data: AddItemRequest, db: Session = Depends(get_db)):
    cart = obtener_carrito(db, cart_id)
    if not cart or cart.status != "open":
        raise HTTPException(status_code=404, detail="Carrito no disponible")

    product = buscar_producto(db, product_id=data.product_id, code=data.code, barcode=data.barcode)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")

    if product.Stock is not None and float(product.Stock) < float(data.quantity):
        raise HTTPException(status_code=400, detail="Stock insuficiente")

    item = agregar_item(db, cart_id, product, data.quantity)
    return CartItemSchema.from_orm(item)

@router.get("/{cart_id}", response_model=CartSchema)
def obtener_carrito_endpoint(cart_id: int, db: Session = Depends(get_db)):
    cart = obtener_carrito(db, cart_id)
    if not cart:
        raise HTTPException(status_code=404, detail="Carrito no encontrado")
    total = sum(i.subtotal for i in cart.items)
    cart_schema = CartSchema.from_orm(cart)
    return cart_schema.model_dump() | {"total": total}