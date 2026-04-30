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

from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain.tools import tool

router = APIRouter(tags=["Chat"])

class ChatMessage(BaseModel):
    message: str
    conversation_history: List[Dict[str, Any]] = []

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://akashkumarsenthilkumar_db_user:mTnLH54vQAmmNjir@yelp.wvxiqvo.mongodb.net/?retryWrites=true&w=majority&appName=yelp")
DB_NAME = os.getenv("DB_NAME", "yelp_db")

def get_mongo_db():
    client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
    return client[DB_NAME]

def serialize_restaurant(r):
    r["id"] = str(r.pop("_id"))
    for k, v in list(r.items()):
        if isinstance(v, ObjectId):
            r[k] = str(v)
        elif isinstance(v, datetime):
            r[k] = v.isoformat()
    return r

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

        words = [w.strip() for w in query.split() if len(w.strip()) > 2]
        if words:
            for word in words:
                search_query["$or"].extend([
                    {"cuisine_type": {"$regex": word, "$options": "i"}},
                    {"description": {"$regex": word, "$options": "i"}},
                    {"amenities": {"$regex": word, "$options": "i"}},
                ])

        results = list(restaurants.find(search_query).limit(5))

        if not results:
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
            desc = (r.get('description', '') or '')[:100]
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
        db = get_mongo_db()
        user_id = user.get('id') or user.get('sub')

        prefs = None
        if user_id:
            try:
                query = {"user_id": user_id}
                if ObjectId.is_valid(user_id):
                    query = {"$or": [{"user_id": user_id}, {"user_id": ObjectId(user_id)}]}
                prefs = db['preferences'].find_one(query)
                if prefs:
                    prefs.pop('_id', None)
            except Exception:
                pass

        prefs_str = json.dumps(prefs) if prefs else "No specific preferences saved."
        safe_prefs = prefs_str.replace("{", "{{").replace("}", "}}")

        llm = ChatGroq(
            model="llama-3.1-8b-instant",
            groq_api_key=os.getenv("GROQ_API_KEY"),
            temperature=0.7
        )

        tools = [search_local_restaurants]
        tavily_key = os.getenv("TAVILY_API_KEY")
        if tavily_key and "YourAPIKeyHere" not in tavily_key:
            try:
                tavily_tool = TavilySearchResults(k=3)
                tools.append(tavily_tool)
            except Exception as e:
                print(f"Failed to initialize Tavily: {e}")

        tool_names = ", ".join([t.name for t in tools])
        tool_descriptions = "\n".join([f"{t.name}: {t.description}" for t in tools])

        prompt = PromptTemplate.from_template(
            "You are Yelp Assistant, a helpful restaurant discovery AI.\n"
            f"User preferences: {safe_prefs}\n\n"
            "You have access to these tools:\n"
            f"{tool_descriptions}\n\n"
            "Use this exact format:\n"
            "Thought: think about what to do\n"
            "Action: tool name (must be one of: " + tool_names + ")\n"
            "Action Input: input string for the tool\n"
            "Observation: tool result\n"
            "... (you may repeat Thought/Action/Observation)\n"
            "Thought: I now have enough to answer\n"
            "Final Answer: your helpful conversational response\n\n"
            "Question: {input}\n"
            "Thought:{agent_scratchpad}"
        )

        agent = create_react_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=4
        )

        result = agent_executor.invoke({"input": data.message})

        unique_restaurants = []
        seen_ids = set()
        for r in found_restaurants_store:
            rid = r.get('id')
            if rid and rid not in seen_ids:
                unique_restaurants.append(r)
                seen_ids.add(rid)

        return {
            "response": result.get("output", "Sorry, I could not generate a response."),
            "restaurants": unique_restaurants
        }

    except Exception as e:
        print("Chatbot Agent Error:", e)
        raise HTTPException(status_code=500, detail=str(e))