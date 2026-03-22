# Yelp Prototype - Restaurant Discovery & Review Platform

A full-stack Yelp-style restaurant discovery and review platform with an **AI Assistant** (LangChain + **Azure OpenAI** + **Tavily** web search) and **Azure Blob** restaurant photos, built with React and FastAPI.

**Course:** DATA 236 | **Lab 1** | Spring 2026

**Team:** **Akash Kumar** (frontend) · **Utkarsh Sharma** (backend)

**Repository:** `https://github.com/Utkarshs9924/yelp-prototype`

---

## Spin up from scratch (team — recommended)

Follow these steps to run the project **without** installing MySQL locally. The app uses a **shared Azure MySQL** database, **Azure OpenAI** for the chat agent, and **Tavily** for optional real-time web search in the AI Assistant and ChatBot.

### 1. Clone the repository

```bash
git clone https://github.com/Utkarshs9924/yelp-prototype.git
cd yelp-prototype
```

> If you cloned into a folder named `yelp-teammate` or similar, `cd` into that folder instead — the important part is you are at the **project root** (where `requirements.txt`, `backend/`, and `frontend/` live).

### 2. Configure environment variables

Create **`backend/.env`** (copy from `backend/.env.example` if you like) with your team’s credentials:

```env
# backend/.env

# Azure MySQL (shared hosted database — no local MySQL install needed)
DB_HOST=yelp-db.mysql.database.azure.com
DB_USER=yelpadmin
DB_PASSWORD="<AZURE_MYSQL_PASSWORD>"
DB_NAME=yelp_db

# JWT secret (required for auth — use a long random string)
JWT_SECRET="<generate_a_long_random_string>"

# Azure OpenAI (required for /chat — agent + embeddings)
AZURE_OPENAI_API_KEY="<AZURE_OPENAI_KEY>"
AZURE_OPENAI_ENDPOINT="<AZURE_OPENAI_ENDPOINT>"

# Tavily — real-time web search in the AI Assistant (Lab 1)
TAVILY_API_KEY="<TAVILY_API_KEY>"

# Azure Blob — restaurant photo upload/delete (optional)
AZURE_STORAGE_CONNECTION_STRING="<AZURE_STORAGE_CONNECTION_STRING>"
AZURE_STORAGE_CONTAINER_NAME=restaurant-photos
```

**Notes:**

- Because the team uses a **hosted Azure MySQL** instance, teammates **do not** need to install MySQL, create `yelp_db` locally, or import SQL dumps — the backend connects to the remote database when these variables are set.
- Ask your team lead for `DB_PASSWORD`, Azure OpenAI, **Tavily**, and (if using photos) **Azure Storage** secrets.
- Never commit `backend/.env` to git (it is listed in `.gitignore`).
- Run **`pip install -r requirements.txt`** from the project root inside your venv so `langchain-openai`, `numpy`, `tavily-python`, and `azure-storage-blob` are available — missing deps often show up as `/chat` or restaurant load failures.

### 3. Set up and run the FastAPI backend

From the **project root** (same folder as `requirements.txt`):

**macOS / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cd backend
uvicorn main:app --reload --port 8000
```

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
cd backend
uvicorn main:app --reload --port 8000
```

- API: **http://localhost:8000**
- Interactive docs: **http://localhost:8000/docs**

Leave this terminal running.

### 4. Set up and run the React frontend

Open a **new** terminal tab/window (keep the backend running). From the **project root**:

```bash
cd frontend
npm install
npm run dev
```

- App: **http://localhost:5173** (or **5174** if Vite picks the next free port — use the URL shown in the terminal)

The Vite dev server proxies `/api` to `http://localhost:8000`, so the browser talks only to the frontend URL; the backend reads/writes **Azure MySQL**, runs the **LangChain** agent on **`POST /chat`** (**Azure OpenAI** + optional **Tavily**), and can upload photos to **Azure Blob** when configured.

### 5. You’re done

Open the app URL from the Vite output. You should see restaurants from the shared database. With Azure OpenAI (and ideally **TAVILY_API_KEY**) set, use **Explore → Ask AI Assistant** or the **ChatBot** for local semantic matches plus real-time web context. See **[walkthrough.md](./walkthrough.md)** for verification steps and screenshot ideas.

---

## Local development (optional)

Use this path if you want **MySQL on your machine** (e.g. Homebrew MySQL) and/or **Ollama** instead of Azure OpenAI. The chat route in this repo is configured for **Azure OpenAI**; for fully offline AI you’d need code that matches Ollama (or env-based switching).

### Prerequisites

- Python 3.9+
- Node.js 18+
- MySQL 8.0+ (local)
- Optional: [Ollama](https://ollama.com/) if you adapt the chat backend for local LLMs

### Database

1. Start MySQL.
2. Create schema and seed data, for example:

```bash
mysql -u root -p < mock_data.sql
```

(Adjust user/password and path as needed. See **Database Schema** below for manual DDL if you prefer.)

### Backend (local DB)

```bash
cd backend
python -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r ../requirements.txt
cp .env.example .env
# Edit .env: DB_HOST=localhost, DB_USER, DB_PASSWORD, DB_NAME=yelp_db, JWT_SECRET=...
```

Optional — seed many restaurants from OpenStreetMap:

```bash
python seed_live_data.py
```

Start the API:

```bash
uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

---

## Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| Python 3.9+ | Runtime |
| FastAPI | REST API framework |
| MySQL | Relational database (local or Azure) |
| mysql-connector-python | Database driver |
| Pydantic | Request/response validation |
| bcrypt | Password hashing |
| PyJWT | JWT token authentication |
| LangChain + langchain-openai | Chat agent on `/chat` (Azure OpenAI tools) |
| langchain-community + tavily-python | Tavily web search tool when `TAVILY_API_KEY` is set |
| numpy | Cosine similarity for local semantic restaurant search |
| azure-storage-blob | Restaurant images in Azure Blob (`utils/blob_storage.py`) |

### Frontend
| Technology | Purpose |
|---|---|
| React 19 | UI framework |
| Vite 8 | Build tool & dev server |
| TailwindCSS 4 | Utility-first CSS framework |
| React Router DOM 7 | Client-side routing |
| Axios | HTTP client for API calls |
| React Icons | Icon library |
| React Hot Toast | Toast notifications |

---

## Features

### User Features
- **Signup / Login** with JWT authentication and bcrypt password hashing
- **Profile management** - update name, phone, about me, city, country, languages, gender
- **Restaurant search** - browse all restaurants, search by name/cuisine/city
- **Restaurant detail view** - photos (incl. Azure Blob upload/delete when configured), contact info, hours, amenities, **Menu** tab, reviews
- **Write/edit/delete reviews** with 1-5 star ratings
- **Favourites** - save and manage favourite restaurants
- **User history** - view past reviews and restaurants added
- **Preferences** - set cuisine, price range, dietary needs, ambiance, and sort preferences for AI recommendations
- **AI Assistant** - LangChain agent on Explore: **local DB** semantic search + **Tavily** real-time web search + user **preferences** in context (Azure OpenAI + `TAVILY_API_KEY` in `.env`)

### Restaurant Owner Features
- **Owner dashboard** - analytics with total restaurants, reviews, average rating, and per-restaurant rating distribution
- **Manage restaurants** - edit restaurant details, upload photos
- **View reviews** - read-only view of reviews for owned restaurants
- **Submit new restaurants** - pending admin approval workflow

### Admin Features
- **Admin control panel** - approve/reject pending owner profiles and restaurant submissions
- **Assign/deassign** restaurant ownership

### AI Chatbot
**Explore** has **Standard Search** and **Ask AI Assistant**; a floating **ChatBot** uses the same backend. **`POST /chat`** runs a **LangChain** OpenAI-functions agent: it can call **`search_local_restaurants`** (embeddings over your MySQL catalog) and, when **`TAVILY_API_KEY`** is configured, **`tavily_search_results_json`** for up-to-date web information (e.g. 2024–2025 food blog–style answers). The response includes assistant text plus **`restaurants`** from the local tool for the UI cards.

---

## Project Structure

```
yelp-prototype/
├── walkthrough.md             # Lab verification: Tavily, Menu, Blob photos
├── mock_data.sql              # Optional local DB seed
├── backend/
│   ├── .env.example           # Environment variable template
│   ├── database.py            # MySQL connection helper
│   ├── auth.py                # JWT token creation & verification, RBAC
│   ├── main.py                # FastAPI app entry point, router registration
│   ├── test_fetch.py          # DB connectivity test script
│   ├── utils/
│   │   └── blob_storage.py    # Azure Blob upload/delete helpers
│   └── routes/
│       ├── users.py           # Signup, login, profile CRUD, user reviews/restaurants
│       ├── restaurants.py     # Restaurant CRUD, search, menu, photo joins
│       ├── reviews.py         # Review CRUD for restaurants
│       ├── favorites.py       # Add/remove/list favourites (JWT)
│       ├── preferences.py     # User preference CRUD (for AI assistant)
│       ├── chat.py            # LangChain agent: local semantic search + Tavily + Azure OpenAI
│       ├── history.py         # User activity timeline
│       ├── photos.py          # Multipart photo upload/delete (Azure Blob)
│       ├── owner.py           # Owner dashboard, stats, restaurant management
│       └── admin.py           # Admin approval workflows
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── vite.config.js         # Vite config with API proxy to backend
│   └── src/
│       ├── main.jsx           # App entry point with BrowserRouter + AuthProvider
│       ├── App.jsx            # Route definitions
│       ├── index.css           # TailwindCSS import
│       ├── context/
│       │   └── AuthContext.jsx # Auth state management (localStorage + JWT)
│       ├── services/
│       │   └── api.js          # Axios instance, all API endpoint methods
│       ├── components/
│       │   ├── Navbar.jsx      # Responsive nav with role-based links
│       │   ├── ProtectedRoute.jsx # Auth guard with role checking
│       │   ├── RestaurantCard.jsx # Restaurant card with cuisine image fallbacks
│       │   ├── StarRating.jsx  # Interactive/display star rating
│       │   └── ChatBot.jsx     # Floating AI chatbot widget
│       └── pages/
│           ├── auth/
│           │   ├── Login.jsx
│           │   └── Signup.jsx
│           ├── restaurant/
│           │   ├── Explore.jsx          # Search page with AI assistant tab
│           │   ├── RestaurantDetail.jsx # Full restaurant view + reviews
│           │   └── AddRestaurant.jsx    # New restaurant form
│           ├── user/
│           │   ├── Profile.jsx
│           │   ├── Preferences.jsx
│           │   ├── Favourites.jsx
│           │   └── History.jsx
│           ├── owner/
│           │   ├── OwnerDashboard.jsx
│           │   ├── ManageRestaurant.jsx
│           │   └── OwnerReviews.jsx
│           └── admin/
│               └── AdminDashboard.jsx
├── requirements.txt           # Python dependencies
└── .gitignore
```

---

## Database Schema (MySQL)

For **local** setups, run SQL to create tables. The production/Azure database may already exist; align column names with `mock_data.sql` and the routes in `backend/routes/`.

> **Note:** The app uses a table named **`favourites`** (British spelling) in MySQL.

See `mock_data.sql` in the repo or use the DDL in previous revisions of this README if you need to bootstrap from empty.

---

## API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/signup` | Register a new user or owner |
| POST | `/login` | Login and receive JWT token |

### Users
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users/{user_id}` | Get user profile |
| PUT | `/users/{user_id}` | Update user profile |
| GET | `/users/{user_id}/reviews` | Get user's reviews |
| GET | `/users/{user_id}/restaurants` | Get user's restaurants |

### Restaurants
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/restaurants` | List all restaurants |
| GET | `/restaurants/search` | Search by name, cuisine, city |
| GET | `/restaurants/{id}` | Get restaurant details |
| GET | `/restaurants/{id}/menu` | Menu items for detail **Menu** tab |
| POST | `/restaurants` | Create a restaurant |

### Reviews (JWT for create/update/delete)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/restaurants/{id}/reviews` | Get reviews for a restaurant |
| POST | `/reviews` | Create a review |
| PUT | `/reviews/{id}` | Update a review |
| DELETE | `/reviews/{id}` | Delete a review |

### Favourites (JWT required)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/favorites` | List current user's favourites |
| POST | `/favorites` | Body: `{ "restaurant_id": <id> }` |
| GET | `/favorites/check/{restaurant_id}` | Whether restaurant is favourited |
| DELETE | `/favorites/{restaurant_id}` | Remove favourite |

### History (JWT required)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/history` | Timeline of reviews + restaurants added |

### Preferences (JWT required)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/preferences` | Get current user's preferences |
| PUT | `/preferences` | Update/create preferences |

### AI Chatbot (JWT)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | LangChain agent: local semantic DB search + optional Tavily web search + Azure OpenAI |

### Photos (JWT; Azure Blob when configured)
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/restaurants/{id}/photos` | Upload image (multipart) |
| DELETE | `/photos/{photo_id}` | Remove blob + DB row (authorized users) |

### Owner (JWT + Owner/Admin role)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/owner/restaurants` | Get owner's restaurants |
| GET | `/owner/dashboard` | Get owner analytics |
| POST | `/owner/restaurants` | Submit new restaurant |
| GET | `/owner/restaurants/{id}/reviews` | Get reviews for owned restaurant |

### Admin (JWT + Admin role)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/admin/owners/pending` | List pending owner approvals |
| PUT | `/admin/owners/{id}/approve` | Approve an owner |
| GET | `/admin/restaurants/pending` | List pending restaurants |
| PUT | `/admin/restaurants/{id}/status` | Approve/reject restaurant |
| PUT | `/admin/restaurants/{id}/assign` | Assign owner to restaurant |
| PUT | `/admin/restaurants/{id}/deassign` | Remove owner from restaurant |

---

## Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| User | user@example.com | password123 |
| Owner | owner@example.com | password123 |
| Admin | admin@example.com | password123 |

> These only work if corresponding users exist in the database you connect to (shared Azure or local seed).

---

## Team contributions

- **Utkarsh Sharma (backend):** FastAPI REST API, MySQL (including Azure), JWT authentication, RBAC, **`/chat`** (LangChain + Azure OpenAI + **Tavily** + local embeddings), Azure Blob photo pipeline, owner/admin workflows
- **Akash Kumar (frontend):** React UI with Vite + TailwindCSS, pages (Explore, Restaurant Detail incl. **Menu** tab & photos, Auth, Profile, Preferences, Favourites, History, Owner Dashboard, Admin Panel), responsive design, API integration, AI Assistant + **ChatBot** UI, cuisine image fallbacks

---

## Architecture

```
┌─────────────────┐        ┌─────────────────────┐        ┌──────────────────┐
│   React (Vite)  │──API──▶│  FastAPI (Python)    │──SQL──▶│  MySQL           │
│   :5173 / :5174 │        │  Port 8000           │        │  Local or Azure  │
│                 │        │                      │        └──────────────────┘
│  - TailwindCSS  │        │  - JWT / bcrypt      │
│  - React Router │        │  - LangChain /chat   │──HTTP──▶│  Azure OpenAI    │
│  - Axios        │        │  - Tavily (web)      │──HTTP──▶│  Tavily API      │
└─────────────────┘        └──────────┬──────────┘
                                      │ Blob        ┌──────────────────┐
                                      └────────────▶│  Azure Blob      │
                                                    │  (photos)        │
                                                    └──────────────────┘
```
