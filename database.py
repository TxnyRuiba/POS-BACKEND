from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import IntegrityError
import os

#from dotenv import load_dotenv
#load_dotenv()  # carga variables desde .env       
#DATABASE_URL = os.getenv("postgresql+psycopg2://postgres:Tronquilo7*@localhost:5432/POS")

DATABASE_URL = "postgresql+psycopg2://postgres:Tronquilo7*@localhost:5432/POS"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ------------------ Dependencia DB ------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()