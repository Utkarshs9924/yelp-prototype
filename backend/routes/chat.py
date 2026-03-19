from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import json
from typing import List, Dict, Any
from database import get_db_connection

router = APIRouter(tags=["Chat"])

class ChatMessage(BaseModel):
    message: str
    conversation_history: List[Dict[str, Any]] = []

@router.post("/chat")
def chat_endpoint(data: ChatMessage):
    try:
        from langchain_community.chat_models import ChatOllama
        from langchain.schema import HumanMessage, SystemMessage
        
        llm = ChatOllama(model="llama3.2:latest", temperature=0)
        
        system_msg = """
        You are a Yelp-style restaurant search assistant.
        Extract search filters from the user query. Output ONLY a valid JSON object with keys: 
        'cuisine' (string or null), 'max_price' (integer 1-4 or null), 'city' (string or null).
        Example 1: "I want cheap Mexican in San Francisco" -> {"cuisine": "Mexican", "max_price": 1, "city": "San Francisco"}
        Example 2: "Fancy italian places" -> {"cuisine": "Italian", "max_price": 4, "city": null}
        Example 3: "Sushi near me" -> {"cuisine": "Sushi", "max_price": null, "city": null}
        Do not output any markdown formatting, just the raw JSON object.
        """
        
        filter_response = llm.invoke([SystemMessage(content=system_msg), HumanMessage(content=data.message)])
        raw_json = filter_response.content.strip().strip('`').strip('json').strip()
        try:
            filters = json.loads(raw_json)
        except:
            filters = {}

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        sql = """
        SELECT r.*, GROUP_CONCAT(rp.photo_url) as photos_str 
        FROM restaurants r 
        LEFT JOIN restaurant_photos rp ON r.id = rp.restaurant_id 
        WHERE 1=1
        """
        params = []
        
        if filters.get('cuisine'):
            sql += " AND r.cuisine_type LIKE %s"
            params.append(f"%{filters['cuisine']}%")
        if filters.get('city'):
            sql += " AND r.city LIKE %s"
            params.append(f"%{filters['city']}%")
        if filters.get('max_price'):
            sql += " AND r.pricing_tier <= %s"
            params.append(str(filters['max_price']))
            
        sql += " GROUP BY r.id LIMIT 5"
        cursor.execute(sql, tuple(params))
        results = cursor.fetchall()
        conn.close()

        for r in results:
            r['photos'] = r['photos_str'].split(',') if r.get('photos_str') else []
            r.pop('photos_str', None)

        if not results:
            return {
                "response": "I couldn't find any restaurants matching your exact criteria. Try adjusting your preferences!", 
                "restaurants": []
            }
            
        names = [f"**{r['name']}** ({r['cuisine_type']})" for r in results]
        reply = f"Here are some great options matching your request: {', '.join(names)}. Let me know if you'd like more details on any of them!"
        
        return {"response": reply, "restaurants": results}
        
    except Exception as e:
        print("Chatbot Error:", e)
        raise HTTPException(status_code=500, detail=str(e))
