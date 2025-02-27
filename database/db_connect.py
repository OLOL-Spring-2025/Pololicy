import psycopg2
from dotenv import load_dotenv
import os

load_dotenv('../../.env')

# Connect to ParadeDB
def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT")
        )
    
def init_db():
    try:
        # Connect to ParadeDB
        conn = get_db_connection()
        
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS embeddings (
                id SERIAL PRIMARY KEY,
                content TEXT,
                embedding VECTOR(1536)  -- Assuming OpenAI embeddings (adjust size)
            );""")
        conn.commit()

        print("Connected to ParadeDB and table created successfully!")

    except Exception as e:
        print("Error connecting to ParadeDB:", e)

    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()    