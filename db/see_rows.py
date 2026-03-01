import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()
DB_URI = os.getenv("DB_URI")

def view_data():
    print("Connecting to the database...\n")
    try:
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

        print("=== DATABASE RECORDS ===\n")
        for table in tables:
            table_name = table[0]
            print(f"Table: {table_name}")
            print("=" * (7 + len(table_name)))
            
            # Fetch the first 50 rows from the table
            cur.execute(f"SELECT * FROM {table_name} LIMIT 50")
            rows = cur.fetchall()
            
            # Extract column names from the cursor description for the header
            if cur.description:
                col_names = [desc[0] for desc in cur.description]
                print(" | ".join(col_names))
                print("-" * max(50, len(" | ".join(col_names))))
            
            if not rows:
                print("  (Table is empty)\n")
                continue
            
            # Print each row
            for row in rows:
                # Convert everything to strings to prevent printing errors with JSONB arrays
                row_str = " | ".join(str(item) for item in row)
                print(row_str)
            print("\n")

        cur.close()
        conn.close()
        print("Data extraction complete.")

    except psycopg2.OperationalError as e:
        print(f"Connection failed: {e}")
        print("Hint: Check your GCP Firewall rules. Make sure your current IP is in the 'Authorized Networks'.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    view_data()