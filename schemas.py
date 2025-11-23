from pydantic import BaseModel

class LoginRequest(BaseModel):
    Username: str
    password: str

class RegisterRequest(BaseModel):
    Username: str
    password: str

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