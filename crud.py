from sqlalchemy.orm import Session
from models import Product
from models import User

def get_user_by_username(db: Session, username: str):
    return db.query(User).filter(User.username == username).first()

def create_user(db: Session, username: str, password: str):
    new_user = User(username=username, password=password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def obtener_productos(db: Session):
    return db.query(Product).all()

def obtener_productos_por_categoria(db: Session, categoria: str):
    return db.query(Product).filter(Product.category == categoria).all()