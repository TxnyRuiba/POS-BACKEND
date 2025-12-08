from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from datetime import timedelta
import crud
from schemas import LoginRequest, RegisterRequest, UserSchema
from app.core.security import (
    create_access_token, 
    get_current_user, 
    require_admin,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from models import Users
from pydantic import BaseModel, Field

router = APIRouter(prefix="/users", tags=["Usuarios y Autenticación"])

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user: UserSchema

class UserRoleUpdate(BaseModel):
    role: str = Field(..., alias="Role")

# ------------------ Registro ------------------
@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Registra un nuevo usuario (solo admin puede asignar roles)"""
    user = crud.create_user(db, request.username, request.password)
    return {"message": "Usuario creado exitosamente", "user_id": user.ID}

# ------------------ Login ------------------
@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Autentica un usuario y devuelve un token JWT"""
    user = crud.authenticate_user(db, request.username, request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Crear token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.Username, "role": user.Role},
        expires_delta=access_token_expires
    )
    
    user_data = UserSchema(ID=user.ID, Username=user.Username)
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_data
    }

# ------------------ Perfil del usuario actual ------------------
@router.get("/me", response_model=UserSchema)
def read_users_me(current_user: Users = Depends(get_current_user)):
    """Obtiene la información del usuario autenticado"""
    return UserSchema(ID=current_user.ID, Username=current_user.Username)

# ------------------ Consultar nivel de acceso ------------------
@router.get("/me/role")
def get_my_role(current_user: Users = Depends(get_current_user)):
    """Obtiene el rol del usuario autenticado"""
    return {
        "user_id": current_user.ID,
        "username": current_user.Username,
        "role": current_user.Role
    }

# ------------------ Actualizar rol (solo admin) ------------------
@router.patch("/{user_id}/role", dependencies=[Depends(require_admin)])
def update_role(
    user_id: int, 
    role_data: UserRoleUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """Actualiza el rol de un usuario (solo admin)"""
    user = crud.update_user_role(db, user_id, role_data.role)
    return {
        "message": "Rol actualizado",
        "user_id": user.ID,
        "new_role": user.Role
    }

# ------------------ Listar usuarios (solo admin) ------------------
@router.get("/", dependencies=[Depends(require_admin)])
def list_users(db: Session = Depends(get_db)):
    """Lista todos los usuarios (solo admin)"""
    users = db.query(Users).all()
    return [{"id": u.ID, "username": u.Username, "role": u.Role} for u in users]