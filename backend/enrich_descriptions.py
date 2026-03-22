import os
import json
from dotenv import load_dotenv
import mysql.connector

try:
    import requests
    import wikipedia
    import openai
except ImportError:
    print("Missing dependencies. Run: pip install wikipedia requests openai")
    exit(1)

# Load DB credentials
load_dotenv()

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "Akash#123"), # Hardcoded fallback based on earlier terminal state
        database=os.getenv("DB_NAME", "yelp_db")
    )

def main():
    print("🚀 Starting AI Description Enrichment Pipeline...")
    
    # Initialize
    print("🚀 Starting AI Description Enrichment Pipeline...")
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Fetch a batch of purely mock descriptions to overwrite
    # Limit to 5 at a time for safety and demo purposes, the user can increase this.
    BATCH_SIZE = 5
    cursor.execute("""
        SELECT id, name, cuisine_type, city, description 
        FROM restaurants 
        WHERE description LIKE 'A popular%' 
        LIMIT %s
    """, (BATCH_SIZE,))
    
    restaurants = cursor.fetchall()
    
    if not restaurants:
        print("✅ No mock descriptions found! Everything is already enriched.")
        return

    print(f"Found {len(restaurants)} restaurants with mock descriptions. Enriching...")

    for idx, r in enumerate(restaurants, 1):
        restaurant_id = r['id']
        name = r['name']
        cuisine = r['cuisine_type']
        city = r['city']
        
        # 1. Fetch real-time context from Wikipedia
        search_query = f"{name} {cuisine} {city}"
        try:
            print(f"   -> Searching Wikipedia: '{search_query}'")
            # We search for the best matching page and get a 2-sentence summary
            search_results = wikipedia.search(search_query)
            if search_results:
                search_context = wikipedia.summary(search_results[0], sentences=2)
            else:
                search_context = "No specific online context found in Wikipedia."
        except Exception as e:
            print(f"   -> Search failed or disambiguation: {e}. Proceeding without internet context.")
            search_context = "No specific online context found in Wikipedia."
            
        # 2. Generate rich description using Llama 3.2
        system_prompt = """
        You are a professional restaurant copywriter for a food discovery app based in the Bay Area.
        Your task is to write an engaging, mouth-watering 2-3 sentence description for a restaurant based on its name, cuisine, location, and the provided internet context (if any).
        DO NOT hallucinate obscure menu items not typical of the cuisine. Use a vibrant, upbeat tone.
        NEVER include introduction text like "Here is the description:". Output ONLY the description string.
        """
        
        human_prompt = f"""
        Restaurant Name: {name}
        Cuisine: {cuisine}
        Location: {city}
        Internet Context: {search_context}
        
        Write the description:
        """
        
        try:
            print("   -> Generating description via Azure OpenAI (gpt-4o-mini)...")
            
            from openai import AzureOpenAI
            client = AzureOpenAI(
                api_key=os.getenv("AZURE_OPENAI_API_KEY"),
                api_version="2024-02-15-preview",
                azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
            )
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": human_prompt}
                ],
                temperature=0.3
            )
            
            new_description = response.choices[0].message.content.strip().strip('"').strip()
            
            # Print the difference
            print(f"   -> OLD: {r['description']}")
            print(f"   -> NEW: {new_description}")
            
            # 3. Update the Database
            cursor.execute(
                "UPDATE restaurants SET description = %s WHERE id = %s",
                (new_description, restaurant_id)
            )
            conn.commit()
            print("   -> ✅ Database Updated!")
            
        except Exception as e:
            print(f"   -> Generation failed: {e}")

    conn.close()
    print("\n🎉 Enrichment batch complete! Run this script again to process the next batch.")

if __name__ == "__main__":
    main()
