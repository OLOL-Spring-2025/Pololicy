import openai
import psycopg2
from dotenv import load_dotenv
import os
import json
from database.database import get_db_connection, init_db
# Database connection details
load_dotenv('../../.env')

openai.api_key =os.getenv("OPENAI_API_KEY")
init_db()

#embedding function to get the embedding of the text
# SEE HOW TO USE LAB MACHINE TO EMBEDD WITH THAT EMBEDDING STUFF
def get_openai_embedding(text):
    response = openai.Embedding.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response["data"][0]["embedding"]

#inserting the document into the database with embedding
def insert_document(content):
    embedding = get_openai_embedding(content)

    conn = get_db_connection()
    cursor = conn.cursor()

    sql = "INSERT INTO embeddings (content, embedding) VALUES (%s, %s::vector)"
    cursor.execute(sql, (content, json.dumps(embedding)))

    conn.commit()
    cursor.close()
    conn.close()

# Example usage
#insert_document("This is a test document", [0.1, 0.2, 0.3] + [0.0] * 1533)  # 1536-dimension vector

def search_similar_documents(query_embedding, top_k=5):
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT")
        )        
        cursor = conn.cursor()

        # Convert Python list to PostgreSQL vector format
        vector_str = f"ARRAY{query_embedding}::vector"

        sql = f"""
        SELECT id, content, embedding <=> {vector_str} AS similarity
        FROM documents
        ORDER BY similarity ASC
        LIMIT {top_k};
        """
        cursor.execute(sql)

        results = cursor.fetchall()
        for row in results:
            print(f"ID: {row[0]}, Content: {row[1]}, Similarity: {row[2]}")

    except Exception as e:
        print("Error during search:", e)

    finally:
        cursor.close()
        conn.close()

# Example search (1536-dim OpenAI-style vector)
search_similar_documents([0.1, 0.2, 0.] + [0.0] * 1533)


#we need to store the meta data of the document in the database as well as another column