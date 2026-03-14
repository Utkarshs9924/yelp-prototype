from fastapi import FastAPI
from database import get_db_connection
from passlib.context import CryptContext

from routes import users
from routes import restaurants
from routes import reviews
from routes import favorites
from routes import preferences

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app.include_router(users.router)
app.include_router(restaurants.router)
app.include_router(reviews.router)
app.include_router(favorites.router)
app.include_router(preferences.router)


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