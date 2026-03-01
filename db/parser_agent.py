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
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

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

# --- UPDATED SCHEMAS ---
class FoodItem(BaseModel):
    name: str = Field(description="Main name of the food item")
    cuisine: Optional[str] = Field(description="The cuisine of the dish. Null if unknown.")

class ExtractionResult(BaseModel):
    foods: list[FoodItem] = Field(description="List of extracted food items")
    email_body: str = Field(description="A friendly, concise email message for the user about the specific leftovers.")

def send_gmail_to_everyone(ai_output_list):
    sender_email = "cheesehacksgrabit@gmail.com"
    app_password = "wcdv hxuy atro ndou" 
    
    try:
        print("Connecting to Gmail server...")
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30)
        server.login(sender_email, app_password)
        
        for item in ai_output_list:
            recipient = item.get('email')
            subject = item.get('subject')
            body = item.get('matter')

            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server.send_message(msg)
            print(f"Successfully sent to: {recipient}")

        server.quit()
        print("\nAll emails sent successfully.")

    except Exception as e:
        print(f"SMTP Error: {e}")

def process_new_log(restaurant_name: str, message: str):
    print(f"\nNEW LOG DETECTED: {restaurant_name}")
    
    db = SessionLocal()
    try:
        print(f"Running AI Extraction & Copywriting via {MODEL_NAME}...")
        
        # --- UPDATED PROMPT ---
        system_prompt = (
            "You are an expert food logistics and marketing assistant. "
            "1. Extract food items and their primary cuisines. "
            "2. Write a short, exciting email body (2-3 sentences) inviting the user to come 'Grab It' before it's gone. "
            "Address the user generally (don't use placeholders like [Name]). "
            "Respond ONLY with a valid JSON object matching this structure: "
            "{'foods': [{'name': 'item', 'cuisine': 'type'}], 'email_body': 'Your generated message here'}"
        )
        
        user_prompt = f"Vendor: {restaurant_name}\nRaw message: {message}\nExtract food and draft the email alert."

        completion = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7, # Slightly higher for more creative email writing
            response_format={"type": "json_object"}
        )
        
        raw_json = json.loads(completion.choices[0].message.content)
        extraction = ExtractionResult(**raw_json)

        if not extraction or not extraction.foods:
            print("AI could not identify any food.")
            return

        # Build keywords
        search_keywords = []
        for item in extraction.foods:
            search_keywords.append(item.name.lower())
            if item.cuisine:
                search_keywords.append(item.cuisine.lower())
        search_keywords.append(restaurant_name.lower().replace("'s", "s")) 
        
        print(f"Searching for keywords: {list(set(search_keywords))}")

        matched_users = db.query(DBUser).filter(
            DBUser.preferences.op('?|')(array(list(set(search_keywords))))
        ).all()

        print(f"Found {len(matched_users)} matches!")
        
        email_queue = []
        for user in matched_users:
            # Use the AI-generated email_body and personalize the greeting
            personalized_matter = f"Hi {user.user_name}!\n\n{extraction.email_body}\n\n📍 Location: {restaurant_name}"
            
            email_queue.append({
                "email": user.user_email,
                "subject": f"Fresh Alert from {restaurant_name}!",
                "matter": personalized_matter
            })
        
        if email_queue:
            send_gmail_to_everyone(email_queue)

    except Exception as e:
        print(f"Workflow Failed: {e}")
    finally:
        db.close()

# --- REAL-TIME LISTENER ---
def listen_to_database():
    print(f"Agent Worker (Groq Engine) started. Listening on 'new_log_channel'...")
    conn = psycopg2.connect(DB_URI)
    conn.autocommit = True 
    cur = conn.cursor()
    cur.execute("LISTEN new_log_channel;")

    try:
        while True:
            if select.select([conn], [], [], 5) == ([], [], []):
                pass 
            else:
                conn.poll()
                while conn.notifies:
                    notify = conn.notifies.pop(0)
                    row_data = json.loads(notify.payload)
                    process_new_log(row_data.get("restaurant_name"), row_data.get("message"))
                    print("\nWaiting for next log...")
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    listen_to_database()