from sqlalchemy.orm import Session
from models import Product
from models import Users

def get_user_by_Username(db: Session, Username: str):
    return db.query(Users).filter(Users.Username == Username).first()

def create_user(db: Session,Username: str, Password: str):
    new_user = Users(Username=Username, Password=Password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def obtener_productos(db: Session):
    return db.query(Product).all()

def obtener_productos_por_categoria(db: Session, categoria: str):
    return db.query(Product).filter(Product.category == categoria).all()