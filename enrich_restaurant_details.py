import os
import json
import random
import mysql.connector
from dotenv import load_dotenv
from openai import AzureOpenAI

# Load variables
load_dotenv('backend/.env')

# City to Zip code mapping
CITY_ZIP_MAP = {
    "San Francisco": ["94102", "94103", "94105", "94107", "94108", "94109", "94110"],
    "Sunnyvale": ["94085", "94086", "94087", "94089"],
    "Santa Clara": ["95050", "95051", "95054"],
    "Palo Alto": ["94301", "94303", "94304", "94306"],
    "San Jose": ["95110", "95112", "95113", "95125", "95126"],
    "Berkeley": ["94702", "94703", "94704", "94705"],
    "Oakland": ["94601", "94602", "94606", "94607"],
    "Burlingame": ["94010"],
    "Stanford": ["94305"],
    "Alameda": ["94501", "94502"],
    "Menlo Park": ["94025"],
    "San Carlos": ["94070"],
    "Half Moon Bay": ["94019"],
    "Woodside": ["94062"],
    "Los Altos": ["94022", "94024"],
    "Mountain View": ["94040", "94041", "94043"],
    "Albany": ["94706"],
    "Sausalito": ["94965"],
    "Orinda": ["94563"],
    "Cupertino": ["95014"],
    "San Bruno": ["94066"],
    "Union City": ["94587"],
    "Redwood City": ["94061", "94062", "94063", "94065"],
    "Fremont": ["94536", "94538", "94539", "94555"]
}

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "yelp_db")
    )

def generate_phone():
    return f"+1 {random.randint(200, 999)}-{random.randint(200, 999)}-{random.randint(1000, 9999)}"

from concurrent.futures import ThreadPoolExecutor

def process_restaurant(r, client):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    r_id = r['id']
    name = r['name']
    cuisine = r['cuisine_type']
    city = r['city']
    desc = r['description'] or ""

    print(f"Enriching: {name} ({city})...")

    # Deterministic fields
    state = "CA"
    zip_codes = CITY_ZIP_MAP.get(city, ["94000"])
    zip_code = random.choice(zip_codes)
    phone = generate_phone()

    # AI-generated fields
    system_prompt = """
    You are a restaurant data expert. Based on the restaurant name, cuisine, and description, generate realistic metadata.
    Provide the following in JSON format:
    1. hours_of_operation (string, e.g., "Mon-Fri: 11am-10pm, Sat-Sun: 10am-11pm")
    2. amenities (comma-separated string, e.g., "Outdoor Seating, Wi-Fi, Full Bar, Wheelchair Accessible")
    3. ambiance (single word or short phrase, e.g., "Trendy", "Casual", "Upscale", "Romantic")
    ONLY output the raw JSON.
    """
    
    user_prompt = f"Name: {name}, Cuisine: {cuisine}, City: {city}, Description: {desc}"

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3
        )
        
        ai_data = json.loads(response.choices[0].message.content.strip().strip('```json').strip('```'))
        hours = ai_data.get('hours_of_operation', "Mon-Sun: 11am-9pm")
        amenities = ai_data.get('amenities', "Casual Dining")
        ambiance = ai_data.get('ambiance', "Casual")

        # Update DB
        cursor.execute("""
            UPDATE restaurants 
            SET state = %s, zip_code = %s, phone = %s, hours_of_operation = %s, amenities = %s, ambiance = %s
            WHERE id = %s
        """, (state, zip_code, phone, hours, amenities, ambiance, r_id))
        conn.commit()
        print(f"   -> ✅ Success: {name}")

    except Exception as e:
        print(f"   -> ❌ Failed: {name} - {e}")
    finally:
        cursor.close()
        conn.close()

def enrich_restaurants():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Initialize Azure OpenAI
    client = AzureOpenAI(
        api_key=os.getenv("AZURE_OPENAI_API_KEY"),
        api_version="2024-02-15-preview",
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
    )

    # Fetch restaurants needing enrichment
    cursor.execute("""
        SELECT id, name, cuisine_type, city, description 
        FROM restaurants 
        WHERE hours_of_operation IS NULL OR amenities IS NULL OR ambiance IS NULL
    """)
    restaurants = cursor.fetchall()
    cursor.close()
    conn.close()
    
    print(f"Found {len(restaurants)} restaurants to enrich.")

    with ThreadPoolExecutor(max_workers=5) as executor:
        for r in restaurants:
            executor.submit(process_restaurant, r, client)

    print("Enrichment complete!")

if __name__ == "__main__":
    enrich_restaurants()
