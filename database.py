from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import IntegrityError
#from dotenv import load_dotenv
import os


DATABASE_URL = os.getenv("postgresql+psycopg2://postgres:Tronquilo7*@localhost:5432/POS")
#DATABASE_URL = "postgresql+psycopg2://postgres:Tronquilo7*@localhost:5432/POS"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()