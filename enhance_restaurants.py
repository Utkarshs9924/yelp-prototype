import os
import re
import mysql.connector
from dotenv import load_dotenv

def sanitize_name(name):
    # Remove non-alphanumeric characters (except spaces)
    name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
    # Lowercase and replace spaces with hyphens
    return name.lower().replace(' ', '-')

def enhance_restaurants():
    load_dotenv('backend/.env')

    try:
        db = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'yelp_db')
        )
        cursor = db.cursor()

        # Fetch restaurants with missing email or website
        cursor.execute("SELECT id, name FROM restaurants WHERE email IS NULL OR website IS NULL")
        restaurants = cursor.fetchall()

        print(f"Found {len(restaurants)} restaurants to enhance.")

        for restaurant_id, name in restaurants:
            sanitized = sanitize_name(name)
            email = f"info@{sanitized}.com"
            website = f"www.{sanitized}.com"

            cursor.execute(
                "UPDATE restaurants SET email = %s, website = %s WHERE id = %s",
                (email, website, restaurant_id)
            )

        db.commit()
        print(f"Successfully enhanced {len(restaurants)} restaurants.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if 'db' in locals() and db.is_connected():
            cursor.close()
            db.close()

if __name__ == "__main__":
    enhance_restaurants()
