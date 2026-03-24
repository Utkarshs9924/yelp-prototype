import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv('backend/.env')

# ADLS Base URL
ACCOUNT_NAME = "yelpclonephotos"
CONTAINER_NAME = "restaurant-photos"
BASE_URL = f"https://{ACCOUNT_NAME}.blob.core.windows.net/{CONTAINER_NAME}"

# Cuisine to ADLS Map
CUISINE_ASSET_MAP = {
    'Pizza': 'traditional_pasta_review_photo_3_1774302771097.png',
    'Mexican': 'tacos_platter_review_photo_4_1774302786282.png',
    'Italian': 'traditional_pasta_review_photo_3_1774302771097.png',
    'Japanese': 'sushi_platter_review_photo_2_1774302757257.png',
    'Sushi': 'sushi_platter_review_photo_2_1774302757257.png',
    'Chinese': 'dim_sum_review_photo_6_1774302824990.png',
    'Thai': 'dim_sum_review_photo_6_1774302824990.png',
    'Burger': 'gourmet_burger_review_photo_1_1774302742382.png',
    'Chicken': 'fried_chicken_review_photo_9_1774302865083.png',
    'Indian': 'indian_curry_review_photo_8_1774302851319.png',
    'Seafood': 'sushi_platter_review_photo_2_1774302757257.png',
    'American': 'gourmet_burger_review_photo_1_1774302742382.png',
    'Fast Food': 'gourmet_burger_review_photo_1_1774302742382.png',
    'Steakhouse': 'steak_dinner_review_photo_5_1774302802504.png',
    'Dessert': 'chocolate_lava_cake_review_photo_10_1774302875701.png',
    'Bakery': 'avocado_toast_review_photo_7_1774302837757.png',
    'Cafe': 'avocado_toast_review_photo_7_1774302837757.png',
    'Coffee': 'avocado_toast_review_photo_7_1774302837757.png',
    'Bar': 'steak_dinner_review_photo_5_1774302802504.png',
    'Pub': 'steak_dinner_review_photo_5_1774302802504.png'
}

DEFAULT_ASSET = 'gourmet_burger_review_photo_1_1774302742382.png'

def rebuild_photos():
    db = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    cursor = db.cursor(dictionary=True)

    print("Fetching restaurants...")
    cursor.execute("SELECT id, cuisine_type FROM restaurants")
    restaurants = cursor.fetchall()

    for r in restaurants:
        cuisine = r['cuisine_type']
        asset = CUISINE_ASSET_MAP.get(cuisine, DEFAULT_ASSET)
        new_url = f"{BASE_URL}/{asset}"
        
        # Check if restaurant has any photo
        cursor.execute("SELECT id FROM restaurant_photos WHERE restaurant_id = %s LIMIT 1", (r['id'],))
        exists = cursor.fetchone()
        
        if exists:
            # Update existing to ADLS
            cursor.execute("UPDATE restaurant_photos SET photo_url = %s WHERE restaurant_id = %s", (new_url, r['id']))
        else:
            # Insert new
            cursor.execute("INSERT INTO restaurant_photos (restaurant_id, photo_url) VALUES (%s, %s)", (r['id'], new_url))

    db.commit()
    print(f"Update complete for {len(restaurants)} restaurants.")
    db.close()

if __name__ == "__main__":
    rebuild_photos()
