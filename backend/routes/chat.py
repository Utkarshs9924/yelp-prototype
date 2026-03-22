from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import os
import json
import numpy as np
from typing import List, Dict, Any
from database import get_db_connection

router = APIRouter(tags=["Chat"])

class ChatMessage(BaseModel):
    message: str
    conversation_history: List[Dict[str, Any]] = []

def cosine_similarity(a, b):
    """Compute cosine similarity between two vectors."""
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

@router.post("/chat")
def chat_endpoint(data: ChatMessage):
    try:
        from openai import AzureOpenAI
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version="2025-01-01-preview",
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
        )
        
        # ── Step 1: Embed the user's query ──────────────────────────
        embed_response = client.embeddings.create(
            input=data.message,
            model="text-embedding-3-small"
        )
        query_vector = embed_response.data[0].embedding
        
        # ── Step 2: Get all restaurant vectors from DB ──────────────
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT r.id, r.name, r.cuisine_type, r.description, r.address,
                   r.city, r.state, r.zip_code, r.phone, r.email, r.website,
                   r.hours_of_operation, r.pricing_tier, r.amenities, r.ambiance,
                   r.owner_id, r.created_by, r.created_at, r.updated_at, r.status,
                   r.embedding,
                   GROUP_CONCAT(rp.photo_url) as photos_str,
                   COALESCE((SELECT AVG(rv.rating) FROM reviews rv WHERE rv.restaurant_id = r.id), 0) as average_rating,
                   COALESCE((SELECT COUNT(*) FROM reviews rv WHERE rv.restaurant_id = r.id), 0) as review_count
            FROM restaurants r
            LEFT JOIN restaurant_photos rp ON r.id = rp.restaurant_id
            WHERE r.embedding IS NOT NULL
            GROUP BY r.id
        """)
        all_restaurants = cursor.fetchall()
        conn.close()
        
        # ── Step 3: Compute cosine similarity for each restaurant ───
        scored = []
        for r in all_restaurants:
            try:
                emb = r['embedding']
                if isinstance(emb, str):
                    emb = json.loads(emb)
                
                sim = cosine_similarity(query_vector, emb)
                scored.append((sim, r))
            except Exception:
                continue
        
        # Sort by highest similarity
        scored.sort(key=lambda x: x[0], reverse=True)
        
        # Take top 5 results
        top_results = []
        for score, r in scored[:5]:
            r.pop('embedding', None)  # Don't send the giant vector to the frontend
            r['photos'] = r['photos_str'].split(',') if r.get('photos_str') else []
            r.pop('photos_str', None)
            r['similarity_score'] = round(score, 4)
            top_results.append(r)
        
        if not top_results:
            return {
                "response": "I couldn't find any restaurants matching your request. Try a different description!",
                "restaurants": []
            }
        
        # ── Step 4: Generate a smart AI response ────────────────────
        names_list = ", ".join([f"**{r['name']}** ({r['cuisine_type']})" for r in top_results])
        
        summary_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a friendly restaurant recommendation assistant. Write a single short, enthusiastic sentence recommending these restaurants to the user based on what they asked for. Be concise (max 2 sentences)."},
                {"role": "user", "content": f"The user asked: '{data.message}'. The top semantic matches are: {names_list}. Write a quick recommendation."}
            ],
            temperature=0.7
        )
        
        reply = summary_response.choices[0].message.content.strip()
        
        return {"response": reply, "restaurants": top_results}
        
    except Exception as e:
        print("Chatbot Error:", e)
        raise HTTPException(status_code=500, detail=str(e))
