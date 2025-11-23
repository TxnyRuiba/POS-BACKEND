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
    id: int = Field(..., alias="ID")   # 🔧 CAMBIO: alias para columna ID
    username: str = Field(..., alias="Username")

    class Config:
        from_attributes = True   # Pydantic v2 reemplaza orm_mode
        populate_by_name = True

class ProductoSchema(BaseModel):
    Id: int
    Product: str
    Irice: float
    #image: str
    Category: str
    Code: str
    Unit: str

    class Config:
        orm_mode = True