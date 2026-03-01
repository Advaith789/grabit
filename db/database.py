import os
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import JSONB
from dotenv import load_dotenv

load_dotenv()

DB_URI = os.getenv("DB_URI")
if not DB_URI:
    print("Error: DB_URI not found in environment variables.")
    exit(1)

engine = create_engine(DB_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class DBUser(Base):
    __tablename__ = "users"
    user_name = Column(String, index=True)
    user_email = Column(String, primary_key=True, index=True)
    preferences = Column(JSONB, default=list)


class DBRestaurant(Base):
    __tablename__ = "restaurants"
    restaurant_name = Column(String, index=True)
    restaurant_email = Column(String, primary_key=True, index=True)


class DBFood(Base):
    __tablename__ = "foods"
    id = Column(Integer, primary_key=True, autoincrement=True)
    restaurant_name = Column(String, index=True)
    email = Column(String)
    food_item = Column(String)
    cuisine = Column(String)
    quantity = Column(String)
