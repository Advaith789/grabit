import pandas as pd
import matplotlib.pyplot as plt
import psycopg2
from google.cloud import storage
import io
from flask import Response
import sec

def generate_handout_viz(request):
    conn = psycopg2.connect(
        dbname="spottedcow_db",
        user="postgres",
        password=sec.password,
        host=sec.host
    )
    
# 2. Query
    query = "SELECT restaurant_name, COUNT(*) as count FROM public.logs GROUP BY restaurant_name ORDER BY count DESC"
    df = pd.read_sql(query, conn)
    conn.close()

    # 3. Create the Plot
    plt.figure(figsize=(10, 6))
    plt.bar(df['restaurant_name'], df['count'], color='#C5050C') 
    plt.xticks(rotation=45, ha='right')
    plt.title('Daily Food Handout Volume')
    plt.ylabel('Number of Instances')
    plt.tight_layout()

    # 4. Save to a Buffer
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close() 
    buf.seek(0)

    # 5. Return the image directly
    return Response(buf.read(), mimetype='image/png')


if __name__ == "__main__":
    # This simulates a request so you can run it with 'python main.py'
    class MockRequest:
        def get_json(self): return {}
    
    print("Generating local test image...")
    # Call your function
    response = generate_handout_viz(MockRequest())
    
    # Save the result to a file so you can open it
    with open("test_chart.png", "wb") as f:
        f.write(response.data)
    print("Done! Open 'test_chart.png' in your folder to see the graph.")