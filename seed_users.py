import os
import random
import mysql.connector
from dotenv import load_dotenv

def create_mock_users():
    load_dotenv('backend/.env')
    
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'yelp_db')
        )
        cursor = conn.cursor()
        
        first_names = ["James", "Mary", "Robert", "Patricia", "John", "Jennifer", "Michael", "Linda", "David", "Elizabeth"]
        last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
        
        print("Creating 100 extra mock users...")
        for _ in range(100):
            fname = random.choice(first_names)
            lname = random.choice(last_names)
            name = f"{fname} {lname}"
            email = f"{fname.lower()}.{lname.lower()}.{random.randint(10, 999)}@mockmail.com"
            password_hash = "hashed_password" # Mock hash
            
            cursor.execute("""
                INSERT IGNORE INTO users (name, email, password_hash)
                VALUES (%s, %s, %s)
            """, (name, email, password_hash))
        
        conn.commit()
        print("✅ Mock users created!")
        
    except Exception as e:
        print(f"❌ Failed: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    create_mock_users()
