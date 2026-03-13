from fastapi import FastAPI
from pydantic import BaseModel
from database import get_db_connection
from passlib.context import CryptContext

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str


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


@app.post("/signup")
def signup(user: SignupRequest):

    conn = get_db_connection()
    cursor = conn.cursor()

    hashed_password = pwd_context.hash(user.password)

    query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
    cursor.execute(query, (user.name, user.email, hashed_password))

    conn.commit()
    conn.close()

    return {"message": "User created successfully"}