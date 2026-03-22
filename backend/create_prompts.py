import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "yelp_db")
    )

def main():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, cuisine_type FROM restaurants")
        restaurants = cursor.fetchall()
        
        # We need to know starting user ID so the mock user IDs can be referenced by the reviews
        cursor.execute("SELECT MAX(id) as max_id FROM users")
        max_id = cursor.fetchone()['max_id'] or 0
        start_user_id = max_id + 1
        end_user_id = start_user_id + 49
        
        conn.close()
    except Exception as e:
        print("Error connecting to DB:", e)
        return

    output = "# ChatGPT Prompts for Mock Data Generation\n\n"
    output += "Copy and paste the following prompts into your ChatGPT Pro account sequentially. Make sure to paste the generated SQL exacty into your database.\n\n"

    # Step 1: Users
    output += "## Prompt 1: Generate Mock Users\n"
    output += "```text\n"
    output += "Please generate 50 realistic mock users for a Yelp-style restaurant app. "
    output += "Output ONLY a single SQL script composed of 50 `INSERT INTO users (name, email, password_hash, role, city)` statements. "
    output += "Use a generic hash like '$2b$12$eImiTXuWVxfM37uY...example' for the password_hash. "
    output += "Role should be 'user'. City should be variations of major US cities. "
    output += "Output MUST be purely raw SQL formatted cleanly without markdown fences if possible, or inside a single sql block. Do not include any explanations.\n"
    output += "```\n\n"
    
    # Step 2: Reviews
    batch_size = 50
    batch_number = 2
    
    for i in range(0, len(restaurants), batch_size):
        batch = restaurants[i:i+batch_size]
        
        output += f"## Prompt {batch_number}: Generate Mock Reviews (Batch {batch_number - 1})\n"
        output += "```text\n"
        output += f"Please generate 3 highly realistic, 1-to-2 sentence mock restaurant reviews for EACH of the following {len(batch)} restaurants. "
        output += f"The user_id for the reviews should be randomly selected from between {start_user_id} and {end_user_id}. "
        output += "The rating should be between 1 and 5 (mostly 4s and 5s). \n"
        output += "Output ONLY the raw SQL `INSERT INTO reviews (restaurant_id, user_id, rating, comment)` statements for these restaurants. No explanations.\n\n"
        
        output += "List of Restaurants:\n"
        for r in batch:
            output += f"- ID: {r['id']}, Name: \"{r['name']}\", Cuisine: \"{r['cuisine_type']}\"\n"
            
        output += "```\n\n"
        batch_number += 1

    with open("../chatgpt_mock_prompts.md", "w") as f:
        f.write(output)

    print("Successfully generated ../chatgpt_mock_prompts.md")

if __name__ == "__main__":
    main()
