# Lab 1 — Feature walkthrough & verification

Step-by-step checks for **AI Assistant (Tavily + local DB)**, **Menu tab**, and **Azure Blob photos**. Use this for demos, grading evidence, or teammate onboarding.

---

## 0. Run the stack

1. **Backend** (from repo root, with venv activated):

   ```bash
   pip install -r requirements.txt
   cd backend
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

   Use the **same venv** where dependencies are installed; missing packages (e.g. `langchain_openai`, `numpy`) will prevent `/chat` and restaurant tools from loading.

2. **Frontend** (second terminal):

   ```bash
   cd frontend
   npm install
   npm run dev
   ```

   Default URL: **http://localhost:5173**. If that port is busy, Vite may use **5174** — open the URL printed in the terminal.

3. **`backend/.env`** must include at least:
   - `DB_*`, `JWT_SECRET`
   - `AZURE_OPENAI_API_KEY`, `AZURE_OPENAI_ENDPOINT` (for the chat agent)
   - `TAVILY_API_KEY` (for real-time web search in the agent)
   - `AZURE_STORAGE_CONNECTION_STRING` (optional, for photo upload)

---

## 1. Tavily + AI Assistant (real-time web search)

**What was verified:** With a valid **Tavily** API key, the assistant can answer questions that need **up-to-date web context** (e.g. “top sushi spots in San Francisco from 2024 food blogs”) while still using **`search_local_restaurants`** for venues in your MySQL catalog.

**How it works (backend):** `POST /chat` (`backend/routes/chat.py`) runs a **LangChain** OpenAI Functions agent with:

- Tool **`search_local_restaurants`** — Azure embeddings + cosine similarity over `restaurants.embedding`
- Tool **`tavily_search_results_json`** (Tavily) — when `TAVILY_API_KEY` is set and not a placeholder

The system prompt includes the user’s saved **preferences** so the model can mention matches (e.g. Italian prefs) alongside web results.

**Manual test:**

1. Log in as a seeded user (e.g. `user@example.com` if present).
2. Open **Explore → Ask AI Assistant** or use the floating **ChatBot**.
3. Ask something that requires fresh web info, e.g.  
   *“What are highly rated sushi restaurants in San Francisco according to recent food blogs?”*
4. Expect: natural-language reply citing **current** web-style information **and** optional cards for **local DB** matches returned in the JSON payload.

**Evidence (screenshots):** Save captures under `artifacts/` (create the folder if needed), e.g.:

- `artifacts/tavily-ai-assistant-sf-sushi.png` — Explore or ChatBot showing 2024/2025-style recommendations.

> Redact API keys or personal data before sharing screenshots publicly.

---

## 2. Menu tab (restaurant detail)

1. Open any **restaurant detail** page.
2. Select the **Menu** tab.
3. Data comes from **`GET /restaurants/{id}/menu`** (`menu_items` table). Empty table → empty state; the rest of the page still works.

**Evidence:** Screenshot of Menu tab with at least one item (if your DB is seeded).

---

## 3. Azure Blob — photo upload & delete

1. Set **`AZURE_STORAGE_CONNECTION_STRING`** and optionally **`AZURE_STORAGE_CONTAINER_NAME`** in `backend/.env`.
2. On **restaurant detail**, use **upload** to add an image (JPEG/PNG/WebP/GIF, max 10MB).
3. Confirm the image appears in the gallery (URL stored in **`restaurant_photos`**).
4. **Delete** (if your UI exposes it) removes the blob and the DB row for authorized users.

Implementation: `backend/routes/photos.py` + **`backend/utils/blob_storage.py`**.

**Evidence:** Before/after screenshots or short screen recording.

---

## 4. Troubleshooting

| Symptom | Things to check |
|--------|-------------------|
| **Failed to load restaurants** | Backend running on **8000**; DB credentials; browser using correct frontend port (5173 vs 5174). |
| **`/chat` 500 or import errors** | `pip install -r requirements.txt`; `langchain-openai`, `numpy`, `tavily-python` installed in active venv. |
| **No web search in answers** | `TAVILY_API_KEY` missing, invalid, or still set to a placeholder string. |
| **Photo upload 500** | Azure storage env vars; container exists; connection string valid. |

---

## 5. Delivery checklist (Lab 1 alignment)

- [ ] Explore **Standard** search loads restaurants from MySQL  
- [ ] **Ask AI Assistant** + **ChatBot** work with Azure OpenAI  
- [ ] **Tavily** enabled for real-time search when key is configured  
- [ ] **Menu** tab on detail page  
- [ ] **Photos** upload/delete via Azure Blob (when configured)  
- [ ] Screenshots or notes stored for submission (`artifacts/` recommended)  
