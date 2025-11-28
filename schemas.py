from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class LoginRequest(BaseModel):
    username: str = Field(..., alias="Username")
    password: str = Field(..., alias="Password")

    class Config:
        populate_by_name = True


class RegisterRequest(BaseModel):
    username: str = Field(..., alias="Username")
    password: str = Field(..., alias="Password")

    class Config:
        populate_by_name = True

class UserSchema(BaseModel):
    id: int = Field(..., alias="ID")
    username: str = Field(..., alias="Username")

    class Config:
        from_attributes = True   # Pydantic v2 reemplaza orm_mode
        populate_by_name = True


class ProductoCreate(BaseModel):
    code: str | int = Field(..., alias="Code")
    barcode: str | int | None = Field(None, alias="Barcode")
    product: str = Field(..., alias="Product")
    category: str = Field(..., alias="Category")
    units: str = Field(..., alias="Units")
    price: float = Field(..., alias="Price")
    stock: float | int = Field(..., alias="Stock")
    min_stock: float | int = Field(..., alias="Min_Stock")

    model_config = ConfigDict(populate_by_name=True)

class ProductoSchema(BaseModel):
    Id: int = Field(..., alias="Id")
    Code: str | int = Field(..., alias="Code")
    Barcode: str | int | None = Field(None, alias="Barcode")
    Product: str = Field(..., alias="Product")
    Category: str = Field(..., alias="Category")
    Units: str = Field(..., alias="Units")
    Price: float = Field(..., alias="Price")
    Stock: float | int = Field(..., alias="Stock")
    Min_Stock: float | int = Field(..., alias="Min_Stock")
    Activo: int = Field(..., alias="Activo")
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


class ProductoUpdate(BaseModel):
    product: str | None = Field(None, alias="Product")
    code: str | int | None = Field(None, alias="Code")
    barcode: str | int | None = Field(None, alias="Barcode")
    stock: float | int | None = Field(None, alias="Stock")
    min_stock: float | int | None = Field(None, alias="Min_Stock")
    model_config = ConfigDict(populate_by_name=True)

#Carrito

class CartCreate(BaseModel):
    # opcional carritos “vacíos”
    pass

class AddItemRequest(BaseModel):
    product_id: int | None = None
    code: str | None = None
    barcode: str | None = None
    quantity: float = 1.0

class CartItemSchema(BaseModel):
    id: int
    product_id: int
    product_name: str
    price: float
    quantity: float
    subtotal: float

    class Config:
        from_attributes = True

class CartSchema(BaseModel):
    id: int
    status: str
    created_at: datetime | None
    items: list[CartItemSchema] = []
    total: float | None = None

    model_config = ConfigDict(
        from_attributes=True,
    )

class CartUpdateStatus(BaseModel):
    status: str = Field(..., alias="Status")
    model_config = ConfigDict(populate_by_name=True)

class CartUpdateQuantity(BaseModel):
    quantity: int = Field(..., alias="Quantity")
    model_config = ConfigDict(populate_by_name=True)



#Precios
class PrecioUpdate(BaseModel):
    price: float = Field(..., alias="Price")
    reason: str | None = Field(None, alias="Reason")
    model_config = ConfigDict(populate_by_name=True)

class PrecioBulkItem(BaseModel):
    id: int = Field(..., alias="Id")
    price: float = Field(..., alias="Price")
    reason: str | None = Field(None, alias="Reason")
    model_config = ConfigDict(populate_by_name=True)

class PrecioBulkRequest(BaseModel):
    items: list[PrecioBulkItem] = Field(..., alias="Items")
    model_config = ConfigDict(populate_by_name=True)

class ProductoPrecioSchema(BaseModel):
    Id: int
    Code: int
    Product: str
    Price: float
    Activo: int
    model_config = ConfigDict(from_attributes=True)

class PriceHistorySchema(BaseModel):
    id: int
    product_id: int
    old_price: float
    new_price: float
    reason: str | None
    changed_at: datetime
    model_config = ConfigDict(from_attributes=True)