import psycopg2
import json

# Paste your full connection string here
DB_URI = "postgresql://postgres:oaktree301@34.55.89.30/spottedcow_db"

def add_mock_user():
    """Injects a row into the 'users' table."""
    
    # ─── EDIT THIS DATA ──────────────────────────────
    u_name = "Amit Dethe 2"
    u_email = "adehthe2@wisc.edu"
    u_preferences = ["ian's pizza", "pizza"] 
    # ─────────────────────────────────────────────────
    
    print(f"Adding user: {u_name}...")
    try:
        conn = psycopg2.connect(DB_URI)
        cur = conn.cursor()
        
        query = """
            INSERT INTO users (user_name, user_email, preferences) 
            VALUES (%s, %s, %s)
            ON CONFLICT (user_email) DO UPDATE 
            SET user_name = EXCLUDED.user_name, preferences = EXCLUDED.preferences;
        """
        
        cur.execute(query, (u_name, u_email, json.dumps(u_preferences)))
        conn.commit()
        
        print(f"✅ Successfully added/updated user: {u_name} ({u_email})")
        print(f"   Preferences: {u_preferences}\n")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"🚨 Failed to add user: {e}")

def add_mock_restaurant():
    """Injects a row into the 'restaurants' table."""
    
    # ─── EDIT THIS DATA ──────────────────────────────
    r_name = "ian's pizza"
    r_email = "manager@ianspizza.com"
    # ─────────────────────────────────────────────────
    
    print(f"Adding restaurant: {r_name}...")
    try:
        conn = psycopg2.connect(DB_URI)
        cur = conn.cursor()
        
        query = """
            INSERT INTO restaurants (restaurant_name, restaurant_email) 
            VALUES (%s, %s)
            ON CONFLICT (restaurant_email) DO UPDATE 
            SET restaurant_name = EXCLUDED.restaurant_name;
        """
        
        cur.execute(query, (r_name, r_email))
        conn.commit()
        
        print(f"✅ Successfully added/updated restaurant: {r_name} ({r_email})\n")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"🚨 Failed to add restaurant: {e}")

def add_mock_log():
    """Injects a row into the 'logs' table to trigger the AI Worker."""
    
    # ─── EDIT THIS DATA ──────────────────────────────
    r_name = "ian's pizza"
    log_message = "We have 5 large pepperoni pizzas and a tray of breadsticks leftover. Also have biryani! Need someone to grab them ASAP."
    # ─────────────────────────────────────────────────
    
    print(f"Adding log for restaurant: {r_name}...")
    try:
        conn = psycopg2.connect(DB_URI)
        cur = conn.cursor()
        
        query = """
            INSERT INTO logs (restaurant_name, message) 
            VALUES (%s, %s);
        """
        
        cur.execute(query, (r_name, log_message))
        conn.commit()
        
        print(f"✅ Successfully added log for: {r_name}")
        print(f"   Message: '{log_message}'")
        print("   👉 Check your agent_worker.py terminal to see if it triggered!\n")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"🚨 Failed to add log: {e}")


if __name__ == "__main__":
    print("=== DATABASE INJECTION SCRIPT ===\n")
    
    # I've commented out the other two so it just fires the log trigger right now!
    # add_mock_user()
    # add_mock_restaurant()
    add_mock_log()