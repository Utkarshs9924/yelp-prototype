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

class RestaurantCreate(BaseModel):
    name: str
    cuisine_type: str
    address: str
    city: str
    description: str
    contact_info: str
    price_tier: str

class ReviewCreate(BaseModel):
    user_id: int
    restaurant_id: int
    rating: int
    comment: str

class ReviewUpdate(BaseModel):
    rating: int
    comment: str

class FavoriteCreate(BaseModel):
    user_id: int
    restaurant_id: int


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

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/login")
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

@app.post("/restaurants")
def create_restaurant(restaurant: RestaurantCreate):

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO restaurants
    (name, cuisine_type, address, city, description, contact_info, price_tier)
    VALUES (%s,%s,%s,%s,%s,%s,%s)
    """

    cursor.execute(query, (
        restaurant.name,
        restaurant.cuisine_type,
        restaurant.address,
        restaurant.city,
        restaurant.description,
        restaurant.contact_info,
        restaurant.price_tier
    ))

    conn.commit()
    conn.close()

    return {"message": "Restaurant created successfully"}

@app.get("/restaurants")
def get_restaurants():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM restaurants")

    restaurants = cursor.fetchall()

    conn.close()

    return restaurants

@app.get("/restaurants/{restaurant_id}")
def get_restaurant(restaurant_id: int):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = "SELECT * FROM restaurants WHERE id = %s"
    cursor.execute(query, (restaurant_id,))

    restaurant = cursor.fetchone()

    conn.close()

    return restaurant

@app.post("/reviews")
def create_review(review: ReviewCreate):

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO reviews (user_id, restaurant_id, rating, comment)
    VALUES (%s, %s, %s, %s)
    """

    cursor.execute(query, (
        review.user_id,
        review.restaurant_id,
        review.rating,
        review.comment
    ))

    conn.commit()
    conn.close()

    return {"message": "Review created successfully"}

@app.get("/restaurants/{restaurant_id}/reviews")
def get_restaurant_reviews(restaurant_id: int):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT reviews.id, reviews.rating, reviews.comment, reviews.review_date,
           users.name as user_name
    FROM reviews
    JOIN users ON reviews.user_id = users.id
    WHERE reviews.restaurant_id = %s
    """

    cursor.execute(query, (restaurant_id,))
    reviews = cursor.fetchall()

    conn.close()

    return reviews

@app.put("/reviews/{review_id}")
def update_review(review_id: int, review: ReviewUpdate):

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    UPDATE reviews
    SET rating = %s, comment = %s
    WHERE id = %s
    """

    cursor.execute(query, (
        review.rating,
        review.comment,
        review_id
    ))

    conn.commit()
    conn.close()

    return {"message": "Review updated successfully"}

@app.delete("/reviews/{review_id}")
def delete_review(review_id: int):

    conn = get_db_connection()
    cursor = conn.cursor()

    query = "DELETE FROM reviews WHERE id = %s"
    cursor.execute(query, (review_id,))

    conn.commit()
    conn.close()

    return {"message": "Review deleted successfully"}

@app.post("/favorites")
def add_favorite(favorite: FavoriteCreate):

    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    INSERT INTO favorites (user_id, restaurant_id)
    VALUES (%s, %s)
    """

    cursor.execute(query, (
        favorite.user_id,
        favorite.restaurant_id
    ))

    conn.commit()
    conn.close()

    return {"message": "Restaurant added to favorites"}

@app.get("/favorites/{user_id}")
def get_favorites(user_id: int):

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT restaurants.*
    FROM favorites
    JOIN restaurants ON favorites.restaurant_id = restaurants.id
    WHERE favorites.user_id = %s
    """

    cursor.execute(query, (user_id,))
    favorites = cursor.fetchall()

    conn.close()

    return favorites

@app.delete("/favorites/{favorite_id}")
def remove_favorite(favorite_id: int):

    conn = get_db_connection()
    cursor = conn.cursor()

    query = "DELETE FROM favorites WHERE id = %s"
    cursor.execute(query, (favorite_id,))

    conn.commit()
    conn.close()

    return {"message": "Favorite removed"}