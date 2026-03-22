from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import os
import json
import numpy as np
from typing import List, Dict, Any, Optional
from database import get_db_connection
from auth import get_current_user

# Langchain imports
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool

router = APIRouter(tags=["Chat"])

class ChatMessage(BaseModel):
    message: str
    conversation_history: List[Dict[str, Any]] = []

def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0: return 0
    return float(dot / (norm_a * norm_b))

# This list will store restaurants found by the local tool during the current request
found_restaurants_store = []

@tool
def search_local_restaurants(query: str) -> str:
    """
    Search for restaurants in our local database using semantic similarity. 
    Use this when the user asks for recommendations, specific cuisines, or 'where to eat' 
    within our known catalog.
    """
    global found_restaurants_store
    try:
        # 1. Embed the query
        embeddings = AzureOpenAIEmbeddings(
            azure_deployment="text-embedding-3-small",
            openai_api_version="2024-02-01",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY")
        )
        query_vector = embeddings.embed_query(query)
        
        # 2. Get local data
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM restaurants WHERE embedding IS NOT NULL")
        all_restaurants = cursor.fetchall()
        
        # 3. Compute similarities
        scored = []
        for r in all_restaurants:
            emb = r['embedding']
            if isinstance(emb, str): emb = json.loads(emb)
            sim = cosine_similarity(query_vector, emb)
            scored.append((sim, r))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        top_matches = scored[:5]
        
        # 4. Fetch photos and ratings for matches
        results_text = []
        for sim, r in top_matches:
            # Clean up for the LLM
            r.pop('embedding', None)
            
            # Fetch extra details
            cursor.execute("SELECT photo_url FROM restaurant_photos WHERE restaurant_id = %s", (r['id'],))
            r['photos'] = [p['photo_url'] for p in cursor.fetchall()]
            
            cursor.execute("SELECT AVG(rating), COUNT(*) FROM reviews WHERE restaurant_id = %s", (r['id'],))
            row = cursor.fetchone()
            avg = row['AVG(rating)']
            count = row['COUNT(*)']
            r['average_rating'] = float(avg) if avg else 0
            r['review_count'] = count
            
            found_restaurants_store.append(r)
            results_text.append(f"- {r['name']} ({r['cuisine_type']}): {r['description']}. Rating: {r['average_rating']} ({r['review_count']} reviews)")
        
        conn.close()
        return "Found these restaurants in our database:\n" + "\n".join(results_text)
    except Exception as e:
        print(f"Tool Error: {e}")
        return f"Error searching local database: {str(e)}"

@router.post("/chat")
async def chat_endpoint(data: ChatMessage, user: dict = Depends(get_current_user)):
    global found_restaurants_store
    found_restaurants_store = [] # Reset for new request
    
    if not os.getenv("TAVILY_API_KEY"):
        # Graceful fallback or warning if Tavily is missing
        print("WARNING: TAVILY_API_KEY is not set.")
    
    try:
        # 1. Fetch User Preferences
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM preferences WHERE user_id = %s", (user['id'],))
        prefs = cursor.fetchone()
        conn.close()
        
        prefs_str = json.dumps(prefs) if prefs else "No specific preferences saved."
        
        # 2. Initialize LLM & Tools
        llm = AzureChatOpenAI(
            azure_deployment="gpt-4o-mini",
            openai_api_version="2024-02-01",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            temperature=0.7
        )
        
        # Tavily Search Tool (Required by Lab 1 PDF)
        # We only add it if the key exists and isn't a placeholder
        tools = [search_local_restaurants]
        tavily_key = os.getenv("TAVILY_API_KEY")
        if tavily_key and "YourAPIKeyHere" not in tavily_key:
            try:
                tavily_tool = TavilySearchResults(k=3)
                tools.append(tavily_tool)
                print("Tavily Search Tool initialized successfully.")
            except Exception as e:
                print(f"Failed to initialize Tavily: {e}")
        else:
            print("Tavily key missing or placeholder. Skipping web search tool.")
        
        # 3. Build the Agent
        # Note: we must escape curly braces in prefs_str because ChatPromptTemplate 
        # interprets them as input variables.
        safe_prefs = prefs_str.replace("{", "{{").replace("}", "}}")
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are 'Yelp Assistant', a helpful and enthusiastic AI. 
            The current user's saved preferences are: {safe_prefs}.
            
            GUIDELINES:
            1. Use 'search_local_restaurants' to find spots in our database.
            2. If you need real-time info (hours, special events, or trending news) that might not be in our DB, use the 'tavily_search_results_json' tool.
            3. If 'tavily_search_results_json' tool is missing, just rely on our local database.
            4. Always mention if a recommendation matches the user's saved preferences (e.g., 'Matches your preference for Italian!').
            5. Keep responses conversational and concise (max 3 sentences).
            """),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        agent = create_openai_functions_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
        
        # 4. Execute
        result = agent_executor.invoke({
            "input": data.message,
            "chat_history": [] 
        })
        
        # Deduplicate results in store
        unique_restaurants = []
        seen_ids = set()
        for r in found_restaurants_store:
            if r['id'] not in seen_ids:
                unique_restaurants.append(r)
                seen_ids.add(r['id'])
        
        return {
            "response": result["output"],
            "restaurants": unique_restaurants
        }
        
    except Exception as e:
        print("Chatbot Agent Error:", e)
        raise HTTPException(status_code=500, detail=str(e))
