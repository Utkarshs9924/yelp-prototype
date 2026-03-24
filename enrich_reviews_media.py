import os
import random
import mysql.connector
from dotenv import load_dotenv

# Local Review Pool for fast boosting
REVIEW_POOL = [
    "Great food and even better service! Will definitely be back.",
    "The atmosphere here is amazing. Highly recommended for a nice dinner.",
    "One of my favorite spots in the city. The flavors are so authentic.",
    "Good food, reasonable prices, and friendly staff. 5 stars!",
    "A hidden gem! The decor is lovely and the food was delicious.",
    "Everything we ordered was perfect. Can't wait to try more of the menu.",
    "Excellent experience from start to finish. The staff really cares.",
    "Always a solid choice. Consistent quality and great vibe.",
    "Stumbled upon this place and was pleasantly surprised. So good!",
    "Fantastic meal! The attention to detail is impressive."
]

def get_db_connection():
    load_dotenv('backend/.env')
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'yelp_db')
    )

def main():
    db = get_db_connection()
    cursor = db.cursor()
    
    # 1. Get all restaurants that need reviews
    cursor.execute("""
        SELECT id, name, cuisine_type 
        FROM restaurants r
        WHERE (SELECT COUNT(*) FROM reviews rv WHERE rv.restaurant_id = r.id) < 15
    """)
    restaurants = cursor.fetchall()
    
    # 2. Get all user IDs
    cursor.execute("SELECT id FROM users")
    user_ids = [r[0] for r in cursor.fetchall()]
    
    print(f"Boosting {len(restaurants)} restaurants to 15+ reviews using local batching...")
    
    for rid, name, cuisine in restaurants:
        cursor.execute("SELECT COUNT(*) FROM reviews WHERE restaurant_id = %s", (rid,))
        current = cursor.fetchone()[0]
        needed = 15 - current
        
        if needed <= 0: continue
        
        # Batch insert for speed
        values = []
        for _ in range(needed):
            uid = random.choice(user_ids)
            rating = random.randint(3, 5)
            comment = random.choice(REVIEW_POOL)
            values.append((rid, uid, rating, comment))
            
        cursor.executemany("""
            INSERT INTO reviews (restaurant_id, user_id, rating, comment)
            VALUES (%s, %s, %s, %s)
        """, values)
        db.commit()
        print(f"✅ Boosted {name} from {current} to 15.")

    db.close()
    print("ALL RESTAURANTS NOW HAVE 15+ REVIEWS.")

if __name__ == "__main__":
    main()
