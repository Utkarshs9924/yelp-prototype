import os
import random
import requests
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

# Overpass QL query to find restaurants in a bounding box (e.g. Bay Area)
OVERPASS_URL = "http://overpass-api.de/api/interpreter"
QUERY = """
[out:json];
node["amenity"="restaurant"](37.3,-122.5,38.0,-121.9);
out 500;
"""

CUISINE_IMAGE_MAP = {
    "Pizza": ["1513104890138-7c749659a591", "1590947132387-15ef4020ae40", "1565299624-0a4ff05ddbb2"],
    "Mexican": ["1565299524944-86dc24727f71", "1551504734591-2fce4d6a695c"],
    "Italian": ["1498579150354-977475b7e2b3", "1604068549290-dea0e4a30536"],
    "Japanese": ["1553621042-f6e147245754", "1579871494447-9811cf80d66c", "1554495902-46fccbb1ebb7"],
    "Sushi": ["1553621042-f6e147245754", "1579871494447-9811cf80d66c"],
    "Chinese": ["1540189549336-e6e99c3679fe", "1564834724105-918b73d1b9e0"],
    "Burger": ["1568901346375-23c9450c58cd", "1550547660-d9450f859349"],
    "Thai": ["1559314809-0d155014e29e"],
    "Indian": ["1585937421606-0d5b1ada5004"],
    "Coffee": ["1497935586351-b67a49e012bf"],
    "Bakery": ["1509440159596-0249088772ff"],
    "Seafood": ["1615141982317-08471384e4f1"],
    "Vegan": ["1512621776951-a57141f2eefd"]
}

GENERIC_IMAGES = [
    "1414235077428-97116960ac16", "1504674900247-0877df9cc836", "1476224203463-9889505c10ad",
    "1559339352-11d035aa65de", "1550966871-3ed3cdb5ed0c", "1481833761820-0509a246d8de"
]

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "yelp_clone")
    )

def seed_data():
    print("Fetching live data from OpenStreetMap (Overpass API)...")
    try:
        response = requests.post(OVERPASS_URL, data={'data': QUERY}, timeout=15)
        response.raise_for_status()
        data = response.json()
        nodes = data.get("elements", [])
        print(f"Fetched {len(nodes)} restaurants from OSM.")
    except Exception as e:
        print(f"Error fetching data: {e}")
        return

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Ensure a dummy owner user exists
    cursor.execute("SELECT id FROM users LIMIT 1")
    owner = cursor.fetchone()
    
    if not owner:
        print("Creating dummy owner user...")
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
            ("Data Seeder", "seed@yelp.local", "hashed_password") # Dummy password
        )
        conn.commit()
        owner_id = cursor.lastrowid
    else:
        owner_id = owner["id"]

    print(f"Using Owner ID: {owner_id}")
    
    # Insert restaurants
    inserted = 0
    for node in nodes:
        tags = node.get("tags", {})
        
        name = tags.get("name")
        if not name:
            continue
            
        cuisine = tags.get("cuisine", "American").split(';')[0].title()
        
        street = tags.get("addr:street", "")
        housenumber = tags.get("addr:housenumber", "")
        address = f"{housenumber} {street}".strip() or "Various Locations"
        
        city = tags.get("addr:city", "San Francisco")
        
        phone = tags.get("phone", "N/A")
        
        # Add some random data for missing OSM fields
        price_tier = str(random.randint(1, 4))
        description = f"A popular {cuisine.lower()} restaurant located in {city}."
        
        try:
            query = """
            INSERT INTO restaurants
            (name, cuisine_type, address, city, description, phone, pricing_tier, created_by)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
            """
            cursor.execute(query, (
                name, cuisine, address, city, description, phone, price_tier, owner_id
            ))
            restaurant_id = cursor.lastrowid
            
            photo_query = "INSERT INTO restaurant_photos (restaurant_id, photo_url) VALUES (%s, %s)"
            
            # Map cuisine to specific image, otherwise generic
            matched_group = None
            for key, images in CUISINE_IMAGE_MAP.items():
                if key.lower() in cuisine.lower():
                    matched_group = images
                    break
            
            if matched_group:
                photo_id = random.choice(matched_group)
            else:
                photo_id = random.choice(GENERIC_IMAGES)
                
            generic_photo_url = f"https://images.unsplash.com/photo-{photo_id}?auto=format&fit=crop&w=800&q=80"
            cursor.execute(photo_query, (restaurant_id, generic_photo_url))
            
            inserted += 1
        except Exception as e:
            print(f"Failed to insert {name}: {e}")

    conn.commit()
    conn.close()
    
    print(f"Successfully seeded {inserted} live restaurants into the database!")

if __name__ == "__main__":
    seed_data()
