from fastapi import FastAPI
from database import get_db_connection

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Yelp Prototype API Running"}

@app.get("/test-db")
def test_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SHOW DATABASES;")
    databases = cursor.fetchall()
    conn.close()
    return {"databases": databases}