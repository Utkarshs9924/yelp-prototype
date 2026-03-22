import os
import json
import random
from dotenv import load_dotenv
import mysql.connector
from openai import AzureOpenAI

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "yelp_db")
    )

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2025-01-01-preview",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

def generate_reviews_batch(restaurants_batch):
    # restaurants_batch is a list of dicts: [{'id': 1, 'name': 'Joe Pizza', 'cuisine_type': 'Italian'}]
    prompt = "Create 3 realistic, Yelp-style reviews for each of the following restaurants. "
    prompt += "Ratings should be between 1 and 5 (mostly 4s and 5s, some 3s, rare 1s/2s). "
    prompt += "Output MUST be a JSON array of objects with keys: 'restaurant_id', 'rating', 'comment'.\n"
    prompt += "Do not include any Markdown formatting, just the raw JSON array.\n\n"
    
    for r in restaurants_batch:
        prompt += f"ID: {r['id']} | Name: {r['name']} | Cuisine: {r['cuisine_type']}\n"
        
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        content = response.choices[0].message.content.strip().strip('`').strip('json').strip()
        return json.loads(content)
    except Exception as e:
        print(f"Error generating batch: {e}")
        return []

def main():
    print("Connecting to database...")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # 1. Generate 50 mock users
    first_names = ["Alex", "Jordan", "Taylor", "Morgan", "Casey", "Riley", "Sam", "Jamie", "Drew", "Avery", "Blake"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    
    print("Generating users...")
    users = []
    sql_statements = ["-- Auto-generated extra mock data for presentation\nUSE yelp_db;\n\n-- Create 50 Mock Users\n"]
    for i in range(1, 51):
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        email = f"user{i}_{random.randint(1000,9999)}@example.com"
        # simple bcrypt hash for "password123"
        pwd_hash = "$2b$12$eImiTXuWVxfM37uY4JANjQ==.examplehashforpassword123"
        city = random.choice(["San Francisco", "New York", "Chicago", "Los Angeles", "Austin"])
        
        sql_statements.append(f"INSERT INTO users (name, email, password_hash, role, city) VALUES ('{name}', '{email}', '{pwd_hash}', 'user', '{city}');\n")
        # we assume these IDs will start auto-incrementing from max(id) + 1. 
        # But to be safe on foreign keys, we should query DB first or let them dynamically insert.
        
    sql_statements.append("\n-- Generate Reviews\n")
    
    # Let's get actual max user ID to assign to reviews so we don't break foreign keys
    cursor.execute("SELECT MAX(id) as max_id FROM users")
    max_user_id = cursor.fetchone()['max_id'] or 0
    starting_new_user_id = max_user_id + 1
    
    # 2. Get restaurants
    cursor.execute("SELECT id, name, cuisine_type FROM restaurants")
    all_restaurants = cursor.fetchall()
    
    print(f"Loaded {len(all_restaurants)} restaurants. Generating reviews via Azure OpenAI (this may take a few minutes)...")
    
    # Batch process 25 restaurants at a time
    batch_size = 25
    for i in range(0, len(all_restaurants), batch_size):
        batch = all_restaurants[i:i+batch_size]
        print(f"Processing batch {i//batch_size + 1} of {(len(all_restaurants)//batch_size)+1}...")
        
        reviews = generate_reviews_batch(batch)
        for rev in reviews:
            r_id = rev.get('restaurant_id')
            rating = rev.get('rating', 4)
            comment = str(rev.get('comment', '')).replace("'", "\\'")
            u_id = random.randint(starting_new_user_id, starting_new_user_id + 49)
            
            sql_statements.append(f"INSERT INTO reviews (restaurant_id, user_id, rating, comment) VALUES ({r_id}, {u_id}, {rating}, '{comment}');\n")
            
    # Write to file
    with open("../extra_mock_data.sql", "w") as f:
        f.writelines(sql_statements)
        
    print("Done! Check extra_mock_data.sql in the root directory.")
    
    conn.close()

if __name__ == "__main__":
    main()
