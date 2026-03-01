from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session
# Crucial: JSONB is explicitly imported and used here
from sqlalchemy.dialects.postgresql import array, JSONB
from pydantic import BaseModel
from typing import List

# Replace with your GCP database details
DATABASE_URL = "postgresql://postgres:oaktree301@34.55.89.30/spottedcow_db"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- Database Models ---
class DBUser(Base):
    __tablename__ = "users"
    user_name = Column(String, index=True)
    user_email = Column(String, primary_key=True, index=True)
    # Explicitly set to JSONB
    preferences = Column(JSONB, default=list) 

class DBRestaurant(Base):
    __tablename__ = "restaurants"
    restaurant_name = Column(String, index=True)
    restaurant_email = Column(String, primary_key=True, index=True)

# 🚨 WARNING: These lines will wipe your GCP database and recreate empty tables 
# with the new column names every time the server restarts! 
# Comment out drop_all() once your schema is finalized.
Base.metadata.create_all(bind=engine)


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"], # Allows your Angular app
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Data Schemas ---
class UserCreate(BaseModel):
    user_name: str
    user_email: str
    preferences: list[str] = []

class RestaurantCreate(BaseModel):
    restaurant_name: str
    restaurant_email: str

class TextPayload(BaseModel):
    restaurant_email: str # Used to identify which restaurant is sending the text
    text: str

class EmailPayload(BaseModel):
    user_email: str

class RestaurantSearchPayload(BaseModel):
    restaurants: list[str]

class UserUpdate(BaseModel):
    user_email: str
    preferences: List[str]

# --- Endpoints ---

@app.post("/users/signup")
def user_signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(DBUser).filter(DBUser.user_email == user.user_email).first()
    
    if db_user:
        return {"message": "User exists", "restaurants": db_user.preferences}
    
    
    lowercased_prefs = [p.lower() for p in user.preferences]

    new_user = DBUser(
        user_name=user.user_name, 
        user_email=user.user_email, 
        preferences=lowercased_prefs
    )
    db.add(new_user)
    db.commit()
    return {"message": "User created", "restaurants": []}

@app.post("/users/details")
def get_user_details(payload: EmailPayload, db: Session = Depends(get_db)):
    db_user = db.query(DBUser).filter(DBUser.user_email == payload.user_email).first()
    
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_name": db_user.user_name,
        "user_email": db_user.user_email,
        "preferences": db_user.preferences
    }


@app.post("/users/update-preferences")
def update_preferences(payload: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(DBUser).filter(DBUser.user_email == payload.user_email).first()
    if db_user:
        lowercased_prefs = [p.lower() for p in payload.preferences]
        
        db_user.preferences = lowercased_prefs
        db.commit()
        return {"status": "success"}
    return {"status": "error", "message": "User not found"}

@app.post("/restaurants/signup")
def restaurant_signup(restaurant: RestaurantCreate, db: Session = Depends(get_db)):
    db_restaurant = db.query(DBRestaurant).filter(DBRestaurant.restaurant_email == restaurant.restaurant_email).first()
    
    if db_restaurant:
        return {"message": "Already exists"}
    

    
    new_restaurant = DBRestaurant(
        restaurant_name=restaurant.restaurant_name.lower(), 
        restaurant_email=restaurant.restaurant_email
    )
    db.add(new_restaurant)
    db.commit()
    return {"message": "Restaurant created"}

@app.get("/restaurants")
def get_all_restaurants(db: Session = Depends(get_db)):
    all_restaurants = db.query(DBRestaurant).all()
    restaurant_list = [
        {"restaurant_name": r.restaurant_name, "restaurant_email": r.restaurant_email} 
        for r in all_restaurants
    ]
    return restaurant_list

@app.post("/restaurant/prompt")
def restaurant_echo(payload: TextPayload, db: Session = Depends(get_db)):
    # 1. Verify restaurant
    db_restaurant = db.query(DBRestaurant).filter(DBRestaurant.restaurant_email == payload.restaurant_email).first()
    if not db_restaurant:
        raise HTTPException(status_code=401, detail="Restaurant not recognized.")
    
    # 2. Insert into logs table (This triggers the AI Agent Worker)
    try:
        db.execute(
            text("INSERT INTO logs (restaurant_name, message) VALUES (:name, :msg)"),
            {"name": db_restaurant.restaurant_name, "msg": payload.text}
        )
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"🚨 Log error: {e}")
        raise HTTPException(status_code=500, detail="Failed to log message.")

    print(f"🚀 Log recorded for {db_restaurant.restaurant_name}")
    return {"status": "Log recorded", "restaurant_name": db_restaurant.restaurant_name}