from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
# Crucial: JSONB is explicitly imported and used here
from sqlalchemy.dialects.postgresql import array, JSONB

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

# --- Endpoints ---

@app.post("/users/signup")
def user_signup(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(DBUser).filter(DBUser.user_email == user.user_email).first()
    
    if db_user:
        return {"message": "User exists", "restaurants": db_user.preferences}
    
    new_user = DBUser(
        user_name=user.user_name, 
        user_email=user.user_email, 
        restaurants=user.preferences
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
        "restaurants": db_user.preferences
    }

@app.post("/restaurants/signup")
def restaurant_signup(restaurant: RestaurantCreate, db: Session = Depends(get_db)):
    db_restaurant = db.query(DBRestaurant).filter(DBRestaurant.restaurant_email == restaurant.restaurant_email).first()
    
    if db_restaurant:
        return {"message": "Already exists"}
    
    new_restaurant = DBRestaurant(
        restaurant_name=restaurant.restaurant_name, 
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
    db_restaurant = db.query(DBRestaurant).filter(DBRestaurant.restaurant_email == payload.restaurant_email).first()
    if not db_restaurant:
        raise HTTPException(status_code=401, detail="Restaurant not recognized.")
    
    print(f"Received text from {db_restaurant.restaurant_name}: {payload.text}")
    return {"printed_text": payload.text}

@app.post("/users/search-by-restaurants")
def get_users_by_restaurant(payload: RestaurantSearchPayload, db: Session = Depends(get_db)):
    # Returns the user_email for users whose JSONB array overlaps with the search payload
    results = db.query(DBUser.user_email).filter(
        DBUser.restaurants.op('?|')(array(payload.restaurants))
    ).all()
    
    email_list = [row[0] for row in results]
    return {"user_emails": email_list}