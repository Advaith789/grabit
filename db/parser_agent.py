import os
import json
import select
import psycopg2
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import JSONB, array
from dotenv import load_dotenv

from google import genai
from google.genai import types

load_dotenv()

# ─── Config & Setup ────────────────────────────────────────────────────────
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "gemini-2.5-flash"

DB_URI = "postgresql://postgres:oaktree301@34.55.89.30/spottedcow_db"
engine = create_engine(DB_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ─── SQLAlchemy Models ─────────────────────────────────────────────────────
class DBUser(Base):
    __tablename__ = "users"
    user_name = Column(String, index=True)
    user_email = Column(String, primary_key=True, index=True)
    preferences = Column(JSONB, default=list) 

# ─── Pydantic Models ───────────────────────────────────────────────────────
class FoodItem(BaseModel):
    name: str = Field(description="Main name of the food item")
    cuisine: Optional[str] = Field(description="The cuisine of the dish. Null if unknown.")
    category: Optional[str] = Field(description="E.g., dairy, protein, carb. Null if unknown.")
    dietary: list[str] = Field(description="List of dietary tags (e.g., vegetarian). Empty list if none.")

class ExtractionResult(BaseModel):
    foods: list[FoodItem] = Field(description="List of extracted food items")

# ─── The Agentic Workflow ──────────────────────────────────────────────────

def process_new_log(restaurant_name: str, message: str):
    print(f"\n🚀 NEW LOG DETECTED: {restaurant_name} posted a message!")
    
    db = SessionLocal()
    try:
        # 1. Ask Gemini to extract the food items and cuisine
        print("🧠 Running AI Extraction...")
        prompt = f"Vendor: {restaurant_name}\nRaw message: {message}\nExtract all food items and determine the cuisine of the dish(es). Do not extract quantities or urgency. For the restaurant name, use the simplest possible version (e.g., 'ians pizza' instead of 'Ian's Pizza on State')."
        
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.1,
                response_mime_type="application/json",
                response_schema=ExtractionResult, 
            ),
        )
        extraction = response.parsed

        if not extraction or not extraction.foods:
            print("❌ AI could not identify any food in the message.")
            return

        # 2. Build the keyword list 
        search_keywords = []
        for item in extraction.foods:
            search_keywords.append(item.name.lower())
            if item.cuisine:
                search_keywords.append(item.cuisine.lower())
                
        search_keywords.append(restaurant_name.lower()) 
        print(f"🔍 Searching DB for keywords: {search_keywords}")

        # 3. The Lightning-Fast Postgres Query
        matched_users = db.query(DBUser).filter(
            DBUser.preferences.op('?|')(array(search_keywords))
        ).all()

        # 4. Send the emails
        print(f"✅ Found {len(matched_users)} matches!")
        for user in matched_users:
            print(f"   📧 [EMAIL SENT] To: {user.user_email} | Hi {user.user_name}, {restaurant_name} just posted: '{message}'")
            
    except Exception as e:
        print(f"🚨 Workflow Failed: {e}")
    finally:
        db.close()

# ─── The Real-Time Listener ────────────────────────────────────────────────

def listen_to_database():
    """Silently listens to PostgreSQL for new row insertions."""
    print(f"🎧 Agent Worker started. Listening for new rows in 'logs' table...")
    
    # We use psycopg2 directly here because it has native LISTEN support
    conn = psycopg2.connect(DB_URI)
    conn.autocommit = True # Required for listening
    cur = conn.cursor()
    cur.execute("LISTEN new_log_channel;")

    try:
        while True:
            # Check for new notifications every 5 seconds
            if select.select([conn], [], [], 5) == ([], [], []):
                pass 
            else:
                conn.poll()
                while conn.notifies:
                    notify = conn.notifies.pop(0)
                    
                    # Postgres sends us the exact row data as a JSON string!
                    row_data = json.loads(notify.payload)
                    r_name = row_data.get("restaurant_name", "Unknown Restaurant")
                    msg = row_data.get("message", "")
                    
                    # Fire the AI workflow!
                    process_new_log(r_name, msg)
                    
                    print("\n🎧 Listening for the next log...")
                    
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Agent Worker...")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    listen_to_database()