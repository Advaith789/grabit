import os
import json
import select
import psycopg2
from groq import Groq
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import JSONB, array
from dotenv import load_dotenv

load_dotenv()

MODEL_NAME = "llama-3.3-70b-versatile"
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

DB_URI = "postgresql://postgres:oaktree301@34.55.89.30/spottedcow_db"
engine = create_engine(DB_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class DBUser(Base):
    __tablename__ = "users"
    user_name = Column(String, index=True)
    user_email = Column(String, primary_key=True, index=True)
    preferences = Column(JSONB, default=list) 

class FoodItem(BaseModel):
    name: str = Field(description="Main name of the food item")
    cuisine: Optional[str] = Field(description="The cuisine of the dish. Null if unknown.")
    category: Optional[str] = Field(description="E.g., dairy, protein, carb. Null if unknown.")
    dietary: list[str] = Field(description="List of dietary tags (e.g., vegetarian). Empty list if none.")

class ExtractionResult(BaseModel):
    foods: list[FoodItem] = Field(description="List of extracted food items")

def process_new_log(restaurant_name: str, message: str):
    print(f"\n🚀 NEW LOG DETECTED: {restaurant_name} posted a message!")
    
    db = SessionLocal()
    try:
        # 1. Ask Groq (Llama 3.3) to extract the food items and cuisine
        print(f"🧠 Running AI Extraction via {MODEL_NAME}...")
        
        # We provide the schema as a string hint for Groq
        system_prompt = (
            "You are a food extraction agent. Your job is to extract food entities and their cuisines. "
            "Respond ONLY with a valid JSON object matching this structure: "
            "{'foods': [{'name': 'item_name', 'cuisine': 'cuisine_type', 'category': 'type', 'dietary': []}]}"
        )
        
        user_prompt = f"Vendor: {restaurant_name}\nRaw message: {message}\nExtract food and simplify the restaurant name for matching."

        completion = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.1,
            response_format={"type": "json_object"} # Forces valid JSON
        )
        
        # Parse response into our Pydantic model
        raw_json = json.loads(completion.choices[0].message.content)
        extraction = ExtractionResult(**raw_json)

        if not extraction or not extraction.foods:
            print("❌ AI could not identify any food in the message.")
            return

        # 2. Build the keyword list 
        search_keywords = []
        for item in extraction.foods:
            search_keywords.append(item.name.lower())
            if item.cuisine:
                search_keywords.append(item.cuisine.lower())
                
        # Use simplified logic for restaurant name
        search_keywords.append(restaurant_name.lower().replace("'s", "s")) 
        print(f"🔍 Searching DB for keywords: {list(set(search_keywords))}")

        # 3. The Lightning-Fast Postgres Query
        matched_users = db.query(DBUser).filter(
            DBUser.preferences.op('?|')(array(list(set(search_keywords))))
        ).all()

        # 4. Send the emails
        print(f"✅ Found {len(matched_users)} matches!")
        for user in matched_users:
            print(f"   📧 [NOTIFICATION] To: {user.user_email} | Hi {user.user_name}, {restaurant_name} has leftovers: '{message}'")
            
    except Exception as e:
        print(f"🚨 Workflow Failed: {e}")
    finally:
        db.close()

# ─── The Real-Time Listener ────────────────────────────────────────────────

def listen_to_database():
    """Silently listens to PostgreSQL for new row insertions via LISTEN/NOTIFY."""
    print(f"🎧 Agent Worker (Groq Engine) started. Listening on 'new_log_channel'...")
    
    conn = psycopg2.connect(DB_URI)
    conn.autocommit = True 
    cur = conn.cursor()
    cur.execute("LISTEN new_log_channel;")

    try:
        while True:
            # Wait for notification with a 5-second timeout
            if select.select([conn], [], [], 5) == ([], [], []):
                pass 
            else:
                conn.poll()
                while conn.notifies:
                    notify = conn.notifies.pop(0)
                    row_data = json.loads(notify.payload)
                    
                    r_name = row_data.get("restaurant_name", "Unknown Restaurant")
                    msg = row_data.get("message", "")
                    
                    process_new_log(r_name, msg)
                    print("\n🎧 Waiting for next log...")
                    
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Agent Worker...")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    listen_to_database()