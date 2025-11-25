from pydantic import BaseModel, Field

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

class ProductoSchema(BaseModel):
    id: int = Field(..., alias="Id")
    code: str | int = Field(..., alias="Code")
    barcode: int | None = Field(..., alias="Barcode")
    product: str = Field(..., alias="Product")
    category: str = Field(..., alias="Category")
    units: str = Field(..., alias="Units")
    price: float = Field(..., alias="Price")
    stock: int | float = Field(..., alias="Stock")
    min_stock: int | float = Field(..., alias="Min_Stock")

    class Config:
        from_attributes = True
        populate_by_name = True

class StockUpdate(BaseModel):
    nuevo_stock: int