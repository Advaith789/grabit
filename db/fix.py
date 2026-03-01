import psycopg2

DB_URI = "postgresql://postgres:oaktree301@34.55.89.30/spottedcow_db"

def fix_logs_table():
    print("Fixing the logs table and triggers...\n")
    try:
        conn = psycopg2.connect(DB_URI)
        cur = conn.cursor()
        
        # 1. Drop the existing table that doesn't have the trigger
        cur.execute("DROP TABLE IF EXISTS logs CASCADE;")

        # 2. Recreate it with the exact structure we need
        cur.execute("""
            CREATE TABLE logs (
                id SERIAL PRIMARY KEY,
                restaurant_name VARCHAR,
                message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        # 3. Create the Postgres Function that broadcasts the payload
        cur.execute("""
            CREATE OR REPLACE FUNCTION notify_new_log()
            RETURNS trigger AS $$
            BEGIN
                -- Broadcasts the newly inserted row as a JSON string
                PERFORM pg_notify('new_log_channel', row_to_json(NEW)::text);
                RETURN NEW;
            END;
            $$ LANGUAGE plpgsql;
        """)

        # 4. Attach the trigger to the table
        cur.execute("""
            CREATE TRIGGER log_trigger
            AFTER INSERT ON logs
            FOR EACH ROW EXECUTE PROCEDURE notify_new_log();
        """)
        
        conn.commit()
        print("✅ Success! The 'logs' table is rebuilt and the trigger is strictly attached.")
        
        cur.close()
        conn.close()
    except Exception as e:
        print(f"🚨 Setup failed: {e}")

if __name__ == "__main__":
    fix_logs_table()