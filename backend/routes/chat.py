from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import os
import json
from typing import List, Dict, Any, Optional
from auth import get_current_user
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from bson import ObjectId
from datetime import datetime

# Langchain imports
from langchain_openai import AzureChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import tool

router = APIRouter(tags=["Chat"])

class ChatMessage(BaseModel):
    message: str
    conversation_history: List[Dict[str, Any]] = []

# MongoDB connection
MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://akashkumarsenthilkumar_db_user:mTnLH54vQAmmNjir@yelp.wvxiqvo.mongodb.net/?retryWrites=true&w=majority&appName=yelp")
DB_NAME = os.getenv("DB_NAME", "yelp_db")

def get_mongo_db():
    client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
    return client[DB_NAME]

def serialize_restaurant(r):
    """Convert MongoDB doc to JSON-serializable dict"""
    r["id"] = str(r.pop("_id"))
    for k, v in r.items():
        if isinstance(v, ObjectId):
            r[k] = str(v)
        elif isinstance(v, datetime):
            r[k] = v.isoformat()
    return r

# Store restaurants found during current request
found_restaurants_store = []


@tool
def search_local_restaurants(query: str) -> str:
    """
    Search for restaurants in our local database using text search.
    Use this when the user asks for recommendations, specific cuisines, or where to eat.
    """
    global found_restaurants_store
    try:
        db = get_mongo_db()
        restaurants = db['restaurants']

        # Build text search query from the user's query words
        words = [w.strip() for w in query.split() if len(w.strip()) > 2]

        search_query = {
            "$or": [
                {"name": {"$regex": query, "$options": "i"}},
                {"cuisine_type": {"$regex": query, "$options": "i"}},
                {"description": {"$regex": query, "$options": "i"}},
                {"city": {"$regex": query, "$options": "i"}},
                {"amenities": {"$regex": query, "$options": "i"}},
                {"ambiance": {"$regex": query, "$options": "i"}},
            ]
        }

        # Add individual word searches
        if words:
            for word in words:
                search_query["$or"].extend([
                    {"cuisine_type": {"$regex": word, "$options": "i"}},
                    {"description": {"$regex": word, "$options": "i"}},
                    {"amenities": {"$regex": word, "$options": "i"}},
                ])

        results = list(restaurants.find(search_query).limit(5))

        if not results:
            # Fallback: return top rated restaurants
            results = list(restaurants.find(
                {"average_rating": {"$gt": 0}}
            ).sort("average_rating", -1).limit(5))

        results_text = []
        for r in results:
            r = serialize_restaurant(r)
            found_restaurants_store.append(r)
            avg = r.get('average_rating', 0)
            count = r.get('review_count', 0)
            cuisine = r.get('cuisine_type', 'Various')
            city = r.get('city', '')
            desc = r.get('description', '')[:100] if r.get('description') else ''
            results_text.append(
                f"- {r['name']} ({cuisine}, {city}): {desc}. Rating: {avg} ({count} reviews)"
            )

        return "Found these restaurants in our database:\n" + "\n".join(results_text)

    except Exception as e:
        print(f"Tool Error: {e}")
        return f"Error searching local database: {str(e)}"


@router.post("/chat")
async def chat_endpoint(data: ChatMessage, user: dict = Depends(get_current_user)):
    global found_restaurants_store
    found_restaurants_store = []

    try:
        # 1. Fetch user preferences from MongoDB
        db = get_mongo_db()
        user_id = user.get('id') or user.get('sub')

        prefs = None
        if user_id:
            try:
                prefs = db['preferences'].find_one({
                    "$or": [
                        {"user_id": user_id},
                        {"user_id": ObjectId(user_id)} if ObjectId.is_valid(user_id) else {"user_id": user_id}
                    ]
                })
                if prefs:
                    prefs.pop('_id', None)
            except Exception:
                pass

        prefs_str = json.dumps(prefs) if prefs else "No specific preferences saved."

        # 2. Initialize LLM
        llm = AzureChatOpenAI(
            azure_deployment="gpt-4o-mini",
            openai_api_version="2024-02-01",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            temperature=0.7
        )

        # 3. Tools
        tools = [search_local_restaurants]
        tavily_key = os.getenv("TAVILY_API_KEY")
        if tavily_key and "YourAPIKeyHere" not in tavily_key:
            try:
                tavily_tool = TavilySearchResults(k=3)
                tools.append(tavily_tool)
            except Exception as e:
                print(f"Failed to initialize Tavily: {e}")

        # 4. Build agent
        safe_prefs = prefs_str.replace("{", "{{").replace("}", "}}")

        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""You are 'Yelp Assistant', a helpful and enthusiastic AI concierge for our restaurant discovery platform.
            The current user's saved preferences are: {safe_prefs}.

            CRITICAL WORKFLOW — follow these steps for EVERY user query:

            STEP 1: ALWAYS call 'search_local_restaurants' first to find matching restaurants in our database.

            STEP 2: If Tavily is available, call 'tavily_search_results_json' to enrich your answer with real-time web context.
            Search for things like current hours, recent reviews, special events for the restaurants you found.

            STEP 3: Combine both sources into a rich, helpful answer:
              - Lead with our database results (name, cuisine, rating, price)
              - Enhance with live web findings if available
              - Flag if a recommendation matches the user's saved preferences
              - Keep responses conversational and under 5 sentences.
            """),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_openai_functions_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

        result = agent_executor.invoke({
            "input": data.message,
            "chat_history": []
        })

        # Deduplicate restaurants
        unique_restaurants = []
        seen_ids = set()
        for r in found_restaurants_store:
            rid = r.get('id')
            if rid and rid not in seen_ids:
                unique_restaurants.append(r)
                seen_ids.add(rid)

        return {
            "response": result["output"],
            "restaurants": unique_restaurants
        }

    except Exception as e:
        print("Chatbot Agent Error:", e)
        raise HTTPException(status_code=500, detail=str(e))