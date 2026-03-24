# Lab 1 — Requirements Audit Report

> Compares every requirement from **Lab1-Yelp.pdf** against what is implemented, then lists all **bonus features** that go beyond the spec.

---

## ✅ Required Features — User (Reviewer)

| # | Requirement | Status | Implementation |
|---|-------------|--------|----------------|
| 1 | **Signup** — name, email, password, bcrypt | ✅ Done | `backend/routes/users.py` → `POST /signup` hashes with `bcrypt`. Frontend: `Signup.jsx` |
| 2 | **Login / Logout** — JWT auth | ✅ Done | `backend/auth.py` issues JWT tokens. `AuthContext.jsx` manages state. Navbar shows logout. |
| 3 | **Profile Page** — display info, upload pic, update fields | ✅ Done | `Profile.jsx` + `PUT /users/profile`. Fields: name, email, phone, about me, city, country, languages, gender. |
| 4 | **User Preferences** — cuisine, price, location, dietary, ambiance, sort | ✅ Done | `Preferences.jsx` + `backend/routes/preferences.py`. Saved to `preferences` table, loaded by AI chatbot on every query. |
| 5 | **Restaurant Search** — name, cuisine, keywords, location | ✅ Done | `Explore.jsx` + `GET /restaurants/search`. Filters: name, cuisine type, city/zip, keywords. |
| 6 | **Restaurant Details View** — all fields, reviews, photos, ratings | ✅ Done | `RestaurantDetail.jsx` + `GET /restaurants/{id}`. Shows name, cuisine, address, hours, contact, average rating, review count, all reviews, and photos. |
| 7 | **Add a Restaurant Listing** — name, cuisine, address, description, photos | ✅ Done | `AddRestaurant.jsx` + `POST /restaurants`. Supports name, cuisine, city, description, contact, hours, photos. |
| 8 | **Reviews** — add/edit/delete own, 1-5 stars, comments, date, photos | ✅ Done | `RestaurantDetail.jsx` (inline review form) + `backend/routes/reviews.py`. CRUD with star rating, comment, server-generated date, optional photo upload. |
| 9 | **Favourites** — mark/unmark, favourites tab | ✅ Done | `Favourites.jsx` + `backend/routes/favorites.py`. Heart icon on restaurant cards. |
| 10 | **User History** — previous reviews/restaurants added | ✅ Done | `History.jsx` + `backend/routes/history.py`. Displays user's review and submission history. |
| 11 | **AI Assistant Chatbot** — accessible on home screen | ✅ Done | `ChatBot.jsx` floating widget + "Ask AI Assistant" toggle on `Explore.jsx`. Prominently displayed on the home/dashboard. |

---

## ✅ Required Features — Restaurant Owner

| # | Requirement | Status | Implementation |
|---|-------------|--------|----------------|
| 1 | **Owner Signup** — name, email, password, restaurant location | ✅ Done | `Signup.jsx` has a role selector (User/Owner). Owner-specific signup via `POST /signup`. |
| 2 | **Owner Login/Logout** — JWT auth | ✅ Done | Same JWT system as users. Role-based Navbar: shows "Owner Dashboard" link for owners. |
| 3 | **Profile Management** — view/update restaurant details | ✅ Done | `ManageRestaurant.jsx` + `backend/routes/owner.py`. Update name, cuisine, description, location, contact, photos, hours. |
| 4 | **Restaurant Posting** — location, description, photos, pricing, amenities | ✅ Done | Owners use `AddRestaurant.jsx` with extended fields for pricing tier and amenities. |
| 5 | **Claim/Manage Restaurant** | ✅ Done | `backend/routes/owner.py` → `POST /owner/claim/{id}`. Admin approval workflow. |
| 6 | **View Reviews** — read-only | ✅ Done | `OwnerReviews.jsx` + `GET /owner/restaurants/{id}/reviews`. Read-only display. |
| 7 | **Owner Dashboard** — analytics, recent reviews | ✅ Done | `OwnerDashboard.jsx` + `backend/routes/owner.py`. Shows analytics and recent reviews for owned restaurants. |

---

## ✅ Backend Requirements

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| Python + FastAPI | ✅ Done | `backend/main.py` runs FastAPI with CORS middleware |
| MySQL Database | ✅ Done | `backend/database.py` connects via `mysql-connector-python`, uses `.env` config |
| **User auth API** (JWT login/signup) | ✅ Done | `backend/routes/users.py` + `backend/auth.py` (PyJWT) |
| **Profile management API** | ✅ Done | `backend/routes/users.py` → `GET/PUT /users/profile` |
| **Preferences API** | ✅ Done | `backend/routes/preferences.py` → `GET/PUT /preferences` |
| **Restaurant posting/management API** | ✅ Done | `backend/routes/restaurants.py` → CRUD endpoints |
| **Restaurant search/filtering API** | ✅ Done | `GET /restaurants/search` with name, cuisine, city, zip, pricing_tier, amenities filters |
| **Reviews CRUD API** | ✅ Done | `backend/routes/reviews.py` → Create, List, Update, Delete (own reviews only) |
| **Owner dashboard API** | ✅ Done | `backend/routes/owner.py` → restaurant analytics, reviews |
| **AI chatbot endpoint** | ✅ Done | `backend/routes/chat.py` → `POST /chat` |
| **Security & error handling** | ✅ Done | JWT-protected endpoints, `Depends(get_current_user)`, proper HTTP exception handling |

---

## ✅ Frontend Requirements

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| **Explore/Search Page** | ✅ Done | `Explore.jsx` — search bar, filter chips, restaurant cards with pagination |
| **Restaurant Details Page** | ✅ Done | `RestaurantDetail.jsx` — hero image, tabs (Reviews, Photos, Menu), ratings |
| **Signup/Login Pages** | ✅ Done | `Login.jsx`, `Signup.jsx` — form validation, error handling, role selector |
| **Profile + Preferences Editor** | ✅ Done | `Profile.jsx`, `Preferences.jsx` — all fields from spec |
| **Add Restaurant Form** | ✅ Done | `AddRestaurant.jsx` — photo upload, full details |
| **Write Review Form** | ✅ Done | Inline in `RestaurantDetail.jsx` — star rating, comment, photo attachment |
| **AI Assistant Interface** | ✅ Done | `ChatBot.jsx` — chat window, conversation history, input field, thinking indicator, quick actions, clickable restaurant cards, "New" conversation button |
| **Owner Pages** | ✅ Done | `OwnerDashboard.jsx`, `ManageRestaurant.jsx`, `OwnerReviews.jsx` |
| **Responsive Design** | ✅ Done | CSS with `clamp()`, media queries, mobile-ready layouts |
| **Axios API Integration** | ✅ Done | `services/api.js` — centralized Axios instance with interceptors |
| **Code Architecture** | ✅ Done | `/components`, `/pages`, `/services`, `/context` — clean separation |

---

## ✅ AI Chatbot Requirements

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| **Loads user preferences from DB** | ✅ Done | `chat.py` → queries `preferences` table on every request |
| **Natural language understanding** | ✅ Done | LangChain agent with GPT-4o-mini interprets free-text queries |
| **Searches restaurant DB with filters** | ✅ Done | `search_local_restaurants` tool → vector similarity search against all 499 restaurant embeddings |
| **Ranks by query + preferences** | ✅ Done | Cosine similarity ranking + preference-aware system prompt |
| **Personalized recommendations** | ✅ Done | System prompt instructs "Flag if a recommendation matches user's saved preferences" |
| **Multi-turn conversations** | ✅ Done | `conversation_history` passed from frontend to backend |
| **Tavily web search** for live context | ✅ Done | `TavilySearchResults` tool → mandatory on every query for hours, events, trending |
| **Chat UI**: conversation history | ✅ Done | `ChatBot.jsx` renders full message history |
| **Chat UI**: input field | ✅ Done | Text input with Enter-to-send |
| **Chat UI**: restaurant cards | ✅ Done | `ChatRestaurantCard` component with photo, name, rating, price — clickable to detail page |
| **Chat UI**: thinking indicator | ✅ Done | Animated bouncing dots with "Assistant is thinking..." |
| **Chat UI**: new conversation | ✅ Done | "New" button clears chat history |
| **Quick action buttons** | ✅ Done | "Find dinner tonight", "Best rated near me", "Vegan options" |

---

## ✅ API Documentation

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| Swagger UI | ✅ Done | FastAPI auto-generates Swagger at `/docs`. All endpoints documented. |

---

## ✅ Git & Submission

| Requirement | Status | Implementation |
|-------------|--------|----------------|
| Detailed commit messages | ✅ Done | 5 logical, well-described commits pushed to `main` |
| No `venv` / `__pycache__` committed | ✅ Done | `.gitignore` excludes them |
| README.md | ✅ Done | Present in repo root |
| Private repo | ✅ Done | Hosted on GitHub |

---

---

# 🌟 Bonus Features (Beyond Lab Requirements)

These features were **NOT** required by the lab spec but were added to elevate the project:

### 1. Azure Cloud Hosting (ADLS + Blob Storage)
- **What**: All restaurant and review photos are hosted on **Azure Data Lake Storage** via Azure Blob Storage
- **Why**: Demonstrates cloud-native architecture instead of local file storage
- **How**: `backend/utils/blob_storage.py` uploads to `yelpclonephotos` container. All photo URLs are Azure Blob CDN links.

### 2. Azure OpenAI (GPT-4o-mini) as the LLM Backend
- **What**: The AI chatbot uses **Azure-hosted GPT-4o-mini** instead of a standard OpenAI API key
- **Why**: Shows enterprise-grade AI integration with Azure's managed OpenAI service
- **How**: `AzureChatOpenAI` from `langchain_openai` with Azure endpoint + deployment name

### 3. Semantic Vector Search (RAG Architecture)
- **What**: Every restaurant has a pre-computed **embedding vector** (1536-dim, `text-embedding-3-small`) stored in MySQL
- **Why**: Enables intelligent semantic matching — "quiet romantic dinner" matches restaurants described as "intimate candlelit ambiance" even without keyword overlap
- **How**: `backend/generate_semantic_vectors.py` generates embeddings. `search_local_restaurants` in `chat.py` computes cosine similarity at query time.

### 4. Hybrid RAG: Local DB + Tavily Web Search
- **What**: Every AI query fires **two tools in parallel**: local vector search AND Tavily web search
- **Why**: Provides both our curated data AND live web context (real hours, events, news) — a true hybrid RAG system 
- **How**: LangChain `AgentExecutor` with mandatory 3-step workflow documented in `tavily_hybrid_search_guide.md`

### 5. Scale: 499 Restaurants, 8,824 Reviews, 109 Users
- **What**: The database contains a **production-scale** dataset, not just 5-10 mock records
- **Why**: Makes the app feel real and demonstrates scalability under load
- **How**: Migration scripts (`enhance_restaurants.py`, `enrich_reviews_media.py`, `seed_users.py`) generate AI-written reviews with realistic distributions

### 6. AI-Generated Review Photos
- **What**: ~3,219 review photos generated by AI and uploaded to Azure ADLS
- **Why**: Creates a visually rich experience where reviews have attached food photos
- **How**: AI-generated food images stored under `reviews/` prefix in Azure Blob Storage, linked in the `photos` table

### 7. AI-Enriched Restaurant Data (GPT-4o-mini)
- **What**: **Hours of operation, amenities, and ambiance** were generated by GPT-4o-mini for all 499 restaurants
- **Why**: Creates realistic, diverse metadata without manual data entry
- **How**: `enrich_restaurant_details.py` calls GPT-4o-mini to generate structured data per cuisine type

### 8. Admin Role & Dashboard
- **What**: A third **Admin** role with approval workflows for owners and restaurants
- **Why**: Demonstrates multi-role RBAC beyond the 2-persona (User + Owner) requirement
- **How**: `AdminDashboard.jsx` + `backend/routes/admin.py`. Admin can approve/reject owner claims and new restaurant submissions.

### 9. Multi-Criteria Filter Bar (Cuisine, Price, Amenities)
- **What**: A visual filter bar on the Explore page with cuisine dropdown, price tier buttons ($-$$$$), and amenity toggles
- **Why**: Provides an intuitive, Yelp-like filtering experience beyond basic keyword search
- **How**: `Explore.jsx` sends `cuisine`, `pricing_tier`, `amenities` params to `GET /restaurants/search`

### 10. Dedicated Photos Tab with Media Sync
- **What**: Restaurant detail page has a **separate "Photos" tab** that aggregates all user-contributed review photos
- **Why**: Separates user media from official gallery, matching real Yelp's information architecture
- **How**: `backend/routes/photos.py` + sync script ensures review photos appear in both the review and the photos tab

### 11. Review Photo Modal with Navigation Arrows
- **What**: Clicking a photo in the gallery opens a **full-screen modal** with left/right navigation arrows
- **Why**: Premium UX that lets users browse the photo gallery without leaving the page
- **How**: `RestaurantDetail.jsx` modal component with arrow key and click navigation

### 12. Role-Based Navbar (User / Owner / Admin)
- **What**: Navbar dynamically shows different links based on the user's role
- **Why**: Clean UX that shows relevant actions — "Owner Dashboard" for owners, "Admin Panel" for admins
- **How**: `Navbar.jsx` reads `user.role` from `AuthContext` and conditionally renders links

### 13. Auto-Login on Signup
- **What**: Users are **automatically logged in** after successful registration
- **Why**: Eliminates friction — no need to re-enter credentials after signing up
- **How**: `POST /signup` returns a JWT token + user object; `Signup.jsx` stores them immediately

### 14. Protected Routes
- **What**: `ProtectedRoute.jsx` component wraps authenticated pages
- **Why**: Prevents unauthorized access to user, owner, and admin pages
- **How**: React Router wrapper checks `AuthContext` state before rendering child components

### 15. Swagger API Documentation (Auto-Generated)
- **What**: FastAPI auto-generates interactive Swagger docs at `/docs`
- **Why**: Lab required either Swagger OR Postman — we have fully interactive, testable docs
- **How**: FastAPI's built-in OpenAPI schema generation with Swagger UI

---

## Summary Table

| Category | Required Items | Completed | Completion |
|----------|---------------|-----------|------------|
| User Features | 11 | 11 | **100%** |
| Owner Features | 7 | 7 | **100%** |
| Backend APIs | 10 | 10 | **100%** |
| Frontend Pages | 8 | 8 | **100%** |
| AI Chatbot | 13 | 13 | **100%** |
| API Docs | 1 | 1 | **100%** |
| Git/Submission | 4 | 4 | **100%** |
| **Total Required** | **54** | **54** | **100%** |
| **Bonus Features** | — | **15** | — |
