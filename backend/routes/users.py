from fastapi import APIRouter
from pydantic import BaseModel
from database import get_db_connection
from passlib.context import CryptContext

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

router = APIRouter(tags=["Users"])


class SignupRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


class UserProfileUpdate(BaseModel):
    name: str
    phone: str
    about_me: str
    city: str
    country: str
    languages: str
    gender: str


@router.post("/signup")
def signup(user: SignupRequest):

    conn = get_db_connection()
    cursor = conn.cursor()

    hashed_password = pwd_context.hash(user.password)

    query = "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)"
    cursor.execute(query, (user.name, user.email, hashed_password))

    conn.commit()
    conn.close()

    return {"message": "User created successfully"}


@router.post("/login")
def login(user: LoginRequest):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM users WHERE email = %s"
    cursor.execute(query, (user.email,))
    db_user = cursor.fetchone()

    conn.close()

    if not db_user:
        return {"message": "User not found"}

    if not pwd_context.verify(user.password, db_user["password"]):
        return {"message": "Invalid password"}

    return {"message": "Login successful"}


@router.get("/users/{user_id}")
def get_user(user_id: int):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM users WHERE id = %s"
    cursor.execute(query, (user_id,))

    user = cursor.fetchone()

    conn.close()

    return user


@router.put("/users/{user_id}")
def update_user(user_id: int, user: UserProfileUpdate):

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    UPDATE users
    SET name=%s,
        phone=%s,
        about_me=%s,
        city=%s,
        country=%s,
        languages=%s,
        gender=%s
    WHERE id=%s
    """

    cursor.execute((
        query
    ), (
        user.name,
        user.phone,
        user.about_me,
        user.city,
        user.country,
        user.languages,
        user.gender,
        user_id
    ))

    conn.commit()
    conn.close()

    return {"message": "Profile updated successfully"}


@router.get("/users/{user_id}/reviews")
def get_user_reviews(user_id: int):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM reviews WHERE user_id = %s"

    cursor.execute(query, (user_id,))
    reviews = cursor.fetchall()

    conn.close()

    return reviews


@router.get("/users/{user_id}/restaurants")
def get_user_restaurants(user_id: int):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM restaurants WHERE created_by_user_id = %s"

    cursor.execute(query, (user_id,))
    restaurants = cursor.fetchall()

    conn.close()

    return restaurants