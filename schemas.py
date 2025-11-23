from pydantic import BaseModel

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str
    password: str
    
class ProductoSchema(BaseModel):
    id: int
    name: str
    price: float
    image: str
    category: str
    code: str
    unit: str

    class Config:
        orm_mode = True