import psycopg2

# Paste your full connection string here (replace x.x.x.x with the real IP)
DB_URI = "postgresql://postgres:oaktree301@34.55.89.30/spottedcow_db"

def view_schema():
    print("Connecting to the database...\n")
    try:
        # psycopg2 can parse the entire URL directly
        conn = psycopg2.connect(DB_URI)
        cur = conn.cursor()

        # Query to get all tables in the public schema
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """)
        tables = cur.fetchall()

        if not tables:
            print("No tables found in the 'public' schema.")
            return

        print("=== DATABASE SCHEMA ===\n")
        for table in tables:
            table_name = table[0]
            print(f"Table: {table_name}")
            print("-" * (7 + len(table_name)))
            
            # Query to get columns and data types
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = %s 
                ORDER BY ordinal_position
            """, (table_name,))
            
            columns = cur.fetchall()
            for col in columns:
                print(f"  - {col[0]}: {col[1]}")
            print("\n")

        cur.close()
        conn.close()
        print("Schema extraction complete.")

    except psycopg2.OperationalError as e:
        print(f" Connection failed: {e}")
        print("Hint: Check your GCP Firewall rules. Make sure your current IP is in the 'Authorized Networks'.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    view_schema()