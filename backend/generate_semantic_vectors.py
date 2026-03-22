import os
import json
import asyncio
import mysql.connector
from openai import AsyncAzureOpenAI
from dotenv import load_dotenv

load_dotenv()

# We need the Async client for massive concurrent generation
client = AsyncAzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version="2025-01-01-preview", 
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "yelp_db")
    )

async def process_restaurant(r, sem, retries=3):
    async with sem:
        for attempt in range(retries):
            try:
                # 1. Generate description and menu
                prompt = f"""
                You are a master culinary writer. For the restaurant '{r['name']}' (Cuisine: {r['cuisine_type']}), generate two things:
                1. An extremely rich, mouth-watering, detailed description of the restaurant (exactly 700 to 800 characters). 
                2. A highly realistic restaurant menu with exactly 15 distinct menu items. Each item must have a name, short delicious description, and a realistic price (e.g., 14.99).
                
                Return ONLY a valid JSON object with EXACTLY this structure:
                {{
                   "long_description": "...",
                   "menu_items": [
                      {{"name": "...", "description": "...", "price": 10.99}}
                   ]
                }}
                """
                
                # Use gpt-4o-mini for text generation
                chat_resp = await client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7,
                    response_format={"type": "json_object"}
                )
                data = json.loads(chat_resp.choices[0].message.content)
                
                # Ensure safe escaping for SQL
                desc = data['long_description'].replace("'", "\\'")
                
                # Combine all text for Semantic Embedding
                embedding_text = f"Restaurant: {r['name']}. Cuisine: {r['cuisine_type']}. Description: {desc}\nMenu:\n"
                menu_sql = []
                for item in data['menu_items']:
                    i_name = item['name'].replace("'", "\\'")
                    i_desc = item['description'].replace("'", "\\'")
                    i_price = float(item['price'])
                    embedding_text += f"- {i_name}: {i_desc}\n"
                    menu_sql.append(f"INSERT INTO menu_items (restaurant_id, name, description, price) VALUES ({r['id']}, '{i_name}', '{i_desc}', {i_price});")
                
                # 2. Generate Semantic Vector
                embed_resp = await client.embeddings.create(
                    input=embedding_text,
                    model="text-embedding-3-small"
                )
                vector = embed_resp.data[0].embedding
                vector_json = json.dumps(vector)
                
                update_sql = f"UPDATE restaurants SET description = '{desc}', embedding = '{vector_json}' WHERE id = {r['id']};"
                
                return [update_sql] + menu_sql
                
            except Exception as e:
                print(f"Attempt {attempt+1} failed for {r['name']}: {e}")
                if attempt == retries - 1:
                    return []
                await asyncio.sleep(2 * (attempt + 1))

async def main():
    print("Preparing schema migrations...")
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Run Schema Upgrades natively
    try:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS menu_items (
            id INT AUTO_INCREMENT PRIMARY KEY,
            restaurant_id INT NOT NULL,
            name VARCHAR(255) NOT NULL,
            description TEXT,
            price DECIMAL(10, 2),
            FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE
        );
        """)
        
        # Check if embedding column exists
        cursor.execute("SHOW COLUMNS FROM restaurants LIKE 'embedding'")
        if not cursor.fetchone():
            cursor.execute("ALTER TABLE restaurants ADD COLUMN embedding JSON;")
            
        conn.commit()
    except Exception as e:
        print("Schema upgrade warning:", e)
        
    cursor.execute("SELECT id, name, cuisine_type FROM restaurants")
    restaurants = cursor.fetchall()
    
    # WE MUST CLEAR OLD MENUS SO WE DON'T DUPLICATE IF SCRIPT IS RE-RUN
    cursor.execute("DELETE FROM menu_items")
    conn.commit()
    conn.close()

    print(f"Generating vectors and menus for {len(restaurants)} restaurants concurrently...")
    
    # Azure OpenAI rate limit protection (15 concurrent requests at a time)
    sem = asyncio.Semaphore(15)
    
    tasks = [process_restaurant(r, sem) for r in restaurants]
    results = await asyncio.gather(*tasks)
    
    # Flatten the SQL statements
    all_sql = []
    for sql_list in results:
        if sql_list:
            all_sql.extend(sql_list)
        
    print(f"Applying {len(all_sql)} massive SQL updates locally...")
    
    # Write to a file for backup
    with open("hybrid_vectors_menus.sql", "w") as f:
        f.write("\n".join(all_sql))
        
    # Execute them
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # We execute them in batches
    batch_size = 500
    for i in range(0, len(all_sql), batch_size):
        batch = all_sql[i:i+batch_size]
        try:
            for query in batch:
                cursor.execute(query)
            conn.commit()
            print(f"Committed DB Batch {i//batch_size + 1}/{len(all_sql)//batch_size + 1}")
        except Exception as e:
            print("Batch execution error:", e)
            
    conn.close()
    print("FINISHED ALL OVERHAULS!")

if __name__ == "__main__":
    asyncio.run(main())
