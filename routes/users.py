from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Users
from schemas import LoginRequest, RegisterRequest, UserSchema
import bcrypt

router = APIRouter(prefix="/api", tags=["Usuarios"])

@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(Users).filter(Users.Username == data.username).first()
    if not user or not bcrypt.checkpw(data.password.encode("utf-8"), user.Password.encode("utf-8")):
        raise HTTPException(status_code=401, detail="Usuario o contraseña incorrectos")
    return {"username": user.Username}

@router.post("/register", response_model=UserSchema)
def register(data: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(Users).filter(Users.Username == data.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="El usuario ya existe")

    hashed_password = bcrypt.hashpw(data.password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    new_user = Users(Username=data.username, Password=hashed_password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return UserSchema.from_orm(new_user)
