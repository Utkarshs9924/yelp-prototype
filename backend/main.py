import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import get_db_connection

from routes import users
from routes import restaurants
from routes import reviews
from routes import favorites
from routes import preferences
from routes import chat
from routes import admin
from routes import owner
from routes import history
from routes import photos

app = FastAPI(title="Yelp Prototype API")

# Allow CORS origins from env or default to localhost for dev
default_origins = "http://localhost:5173,http://127.0.0.1:5173"
origins = os.getenv("ALLOWED_ORIGINS", default_origins).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(restaurants.router)
app.include_router(reviews.router)
app.include_router(favorites.router)
app.include_router(preferences.router)
app.include_router(chat.router)
app.include_router(admin.router)
app.include_router(owner.router)
app.include_router(history.router)
app.include_router(photos.router)


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
