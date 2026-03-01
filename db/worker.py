import json
import select
import psycopg2
from sqlalchemy.dialects.postgresql import array
from database import DB_URI, SessionLocal, DBUser, DBRestaurant, DBFood
from ai_service import extract_food_data
from email_service import send_gmail_to_everyone


def process_new_log(restaurant_name: str, message: str):
    print(f"\nNEW LOG DETECTED: {restaurant_name}")
    db = SessionLocal()

    try:
        # 1. Lookup the restaurant email
        db_restaurant = (
            db.query(DBRestaurant)
            .filter(DBRestaurant.restaurant_name == restaurant_name)
            .first()
        )
        restaurant_email = (
            db_restaurant.restaurant_email if db_restaurant else "unknown"
        )

        # 2. Run AI Extraction
        print("Running AI Extraction and Copywriting...")
        extraction = extract_food_data(restaurant_name, message)

        if not extraction or not extraction.foods:
            print("AI could not identify any food.")
            return

        # 3. Save to DB
        print(f"Saving {len(extraction.foods)} items to the foods table...")
        for item in extraction.foods:
            new_food = DBFood(
                restaurant_name=restaurant_name.strip().lower(),
                email=restaurant_email.strip().lower(),
                food_item=item.name.strip().lower() if item.name else "unknown",
                cuisine=item.cuisine.strip().lower() if item.cuisine else "unknown",
                quantity=item.quantity.strip().lower() if item.quantity else "unknown",
            )
            db.add(new_food)
        db.commit()

        # 4. Find matched users
        search_keywords = []
        for item in extraction.foods:
            search_keywords.append(item.name.strip().lower())
            if item.cuisine:
                search_keywords.append(item.cuisine.strip().lower())
        search_keywords.append(restaurant_name.strip().lower().replace("'s", "s"))

        matched_users = (
            db.query(DBUser)
            .filter(DBUser.preferences.op("?|")(array(list(set(search_keywords)))))
            .all()
        )
        print(f"Found {len(matched_users)} matches!")

        # 5. Queue and Send Emails
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


def listen_to_database():
    print("Agent Worker started. Listening on 'new_log_channel'...")
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
