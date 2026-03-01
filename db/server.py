import os
import json
import select
import psycopg2
from groq import Groq
from pydantic import BaseModel, Field
from typing import Optional
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.dialects.postgresql import JSONB, array
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

load_dotenv()

# --- Config & Setup ---
MODEL_NAME = "llama-3.3-70b-versatile"
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

DB_URI = os.getenv("DB_URI")
if not DB_URI:
    print("Error: DB_URI not found in environment variables.")
    exit(1)

engine = create_engine(DB_URI)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# --- Database Models ---
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
    email = Column(String)  # New Column
    food_item = Column(String)
    cuisine = Column(String)
    quantity = Column(String)


# --- Pydantic AI Schemas ---
class FoodItem(BaseModel):
    name: str = Field(description="Main name of the food item")
    cuisine: Optional[str] = Field(
        description="The cuisine of the dish. Null if unknown."
    )
    quantity: Optional[str] = Field(
        description="The quantity of the food. Null if unknown."
    )


class ExtractionResult(BaseModel):
    foods: list[FoodItem] = Field(description="List of extracted food items")
    email_body: str = Field(
        description="A friendly, concise email message for the user."
    )
    email_subject: str = Field(
        description="An exciting, short subject line for the email."
    )


# --- Email Logic ---
def send_gmail_to_everyone(ai_output_list):
    sender_email = "cheesehacksgrabit@gmail.com"
    app_password = "wcdv hxuy atro ndou"

    try:
        print("Connecting to Gmail server...")
        server = smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30)
        server.login(sender_email, app_password)

        for item in ai_output_list:
            recipient = item.get("email")
            subject = item.get("subject")
            body = item.get("matter")

            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = recipient
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain"))

            server.send_message(msg)
            print(f"Successfully sent to: {recipient}")

        server.quit()
        print("All emails sent successfully.")

    except Exception as e:
        print(f"SMTP Error: {e}")


# --- Agentic Workflow ---
def process_new_log(restaurant_name: str, message: str):
    print(f"\nNEW LOG DETECTED: {restaurant_name}")

    db = SessionLocal()
    try:
        # Lookup the restaurant email to save into the foods table
        db_restaurant = (
            db.query(DBRestaurant)
            .filter(DBRestaurant.restaurant_name == restaurant_name)
            .first()
        )
        restaurant_email = (
            db_restaurant.restaurant_email if db_restaurant else "unknown"
        )

        print(f"Running AI Extraction and Copywriting via {MODEL_NAME}...")

        system_prompt = (
            "You are an expert food logistics and marketing assistant. "
            "1. Extract food items, their primary cuisines, and quantities. "
            "2. Write a short, exciting email body (2-3 sentences). "
            "3. Write a catchy, short email subject line. "
            "Use emojis in the content to show more engaging content. "
            "STRICT RULE 1: The 'quantity' MUST be strictly numerical digits only (e.g., use '10' instead of 'ten', '1' instead of 'a tray'). "
            "STRICT RULE 2: Normalize the 'name' and 'cuisine' fields to be strictly singular and lowercase (e.g., output 'pizza' instead of 'Pizzas' or 'pizzas', 'taco' instead of 'Tacos'). "
            "Respond ONLY with a valid JSON object matching this structure: "
            "{"
            "'foods': [{'name': 'singular item', 'cuisine': 'singular type', 'quantity': 'digits only'}], "
            "'email_body': 'Body text here', "
            "'email_subject': 'Subject line here'"
            "}"
        )

        user_prompt = f"Vendor: {restaurant_name}\nRaw message: {message}\nExtract food and draft the email alert."

        completion = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            response_format={"type": "json_object"},
        )

        raw_json = json.loads(completion.choices[0].message.content)
        extraction = ExtractionResult(**raw_json)

        if not extraction or not extraction.foods:
            print("AI could not identify any food.")
            return

        # --- 1. Save all extracted foods to the database ---
        print(f"Saving {len(extraction.foods)} items to the foods table...")
        for item in extraction.foods:
            new_food = DBFood(
                # Apply strip() and lower() to standardise the data
                restaurant_name=restaurant_name.strip().lower(),
                email=(
                    restaurant_email.strip().lower() if restaurant_email else "unknown"
                ),
                food_item=item.name.strip().lower() if item.name else "unknown",
                cuisine=item.cuisine.strip().lower() if item.cuisine else "unknown",
                quantity=item.quantity.strip().lower() if item.quantity else "unknown",
            )
            db.add(new_food)

        db.commit()
        print("Successfully saved food items to DB.")

        # --- 2. Build keywords for user matching ---
        search_keywords = []
        for item in extraction.foods:
            search_keywords.append(item.name.strip().lower())
            if item.cuisine:
                search_keywords.append(item.cuisine.strip().lower())
        search_keywords.append(restaurant_name.strip().lower().replace("'s", "s"))

        print(f"Searching for keywords: {list(set(search_keywords))}")

        matched_users = (
            db.query(DBUser)
            .filter(DBUser.preferences.op("?|")(array(list(set(search_keywords)))))
            .all()
        )

        print(f"Found {len(matched_users)} matches!")

        # --- 3. Queue and send emails ---
        email_queue = []
        for user in matched_users:
            personalized_matter = f"Hi {user.user_name}!\n\n{extraction.email_body}\n\nLocation: {restaurant_name}"

            email_queue.append(
                {
                    "email": user.user_email,
                    "subject": extraction.email_subject,
                    "matter": personalized_matter,
                }
            )

        if email_queue:
            send_gmail_to_everyone(email_queue)

    except Exception as e:
        db.rollback()
        print(f"Workflow Failed: {e}")
    finally:
        db.close()


# --- Real-Time Listener ---
def listen_to_database():
    print(f"Agent Worker started. Listening on 'new_log_channel'...")

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
                    process_new_log(
                        row_data.get("restaurant_name"), row_data.get("message")
                    )
                    print("\nWaiting for next log...")
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        cur.close()
        conn.close()


if __name__ == "__main__":
    listen_to_database()
