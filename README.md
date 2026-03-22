# Yelp Prototype - Restaurant Discovery & Review Platform

A full-stack Yelp-style restaurant discovery and review platform with an AI-powered recommendation chatbot, built with React and FastAPI.

**Course:** DATA 236 | **Lab 1** | Spring 2026

**Team:** **Akash Kumar** (frontend) · **Utkarsh Sharma** (backend)

**Repository:** `https://github.com/Utkarshs9924/yelp-prototype`

---

## Spin up from scratch (team — recommended)

Follow these steps to run the project **without** installing MySQL locally. The app uses a **shared Azure MySQL** database and **Azure OpenAI** for the AI Assistant (Explore page).

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

# Azure OpenAI (AI Assistant on Explore page)
AZURE_OPENAI_API_KEY="<AZURE_OPENAI_KEY>"
AZURE_OPENAI_ENDPOINT="<AZURE_OPENAI_ENDPOINT>"
```

**Notes:**

- Because the team uses a **hosted Azure MySQL** instance, teammates **do not** need to install MySQL, create `yelp_db` locally, or import SQL dumps — the backend connects to the remote database when these variables are set.
- Ask your team lead for the actual values for `DB_PASSWORD`, `AZURE_OPENAI_API_KEY`, and `AZURE_OPENAI_ENDPOINT`.
- Never commit `backend/.env` to git (it is listed in `.gitignore`).

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

- App: **http://localhost:5173**

The Vite dev server proxies `/api` to `http://localhost:8000`, so the browser talks only to the frontend URL; the frontend talks to your local backend, which reads/writes **Azure MySQL** and calls **Azure OpenAI** for the AI chat route.

### 5. You’re done

Open **http://localhost:5173** in your browser. You should see restaurants from the shared database and be able to use the **Ask AI Assistant** tab on Explore when Azure OpenAI env vars are set correctly.

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
| OpenAI SDK (Azure) | AI Assistant filter extraction (`/chat`) |

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
- **Restaurant detail view** - photos, contact info, hours, amenities, reviews
- **Write/edit/delete reviews** with 1-5 star ratings
- **Favourites** - save and manage favourite restaurants
- **User history** - view past reviews and restaurants added
- **Preferences** - set cuisine, price range, dietary needs, ambiance, and sort preferences for AI recommendations
- **AI Assistant** - natural language search on the Explore page (Azure OpenAI when configured in `.env`)

### Restaurant Owner Features
- **Owner dashboard** - analytics with total restaurants, reviews, average rating, and per-restaurant rating distribution
- **Manage restaurants** - edit restaurant details, upload photos
- **View reviews** - read-only view of reviews for owned restaurants
- **Submit new restaurants** - pending admin approval workflow

### Admin Features
- **Admin control panel** - approve/reject pending owner profiles and restaurant submissions
- **Assign/deassign** restaurant ownership

### AI Chatbot
The Explore page includes **Standard Search** and **Ask AI Assistant**. With `AZURE_OPENAI_API_KEY` and `AZURE_OPENAI_ENDPOINT` set, the backend uses **Azure OpenAI** to turn natural language into JSON filters and runs SQL against the restaurant database.

---

## Project Structure

```
yelp-prototype/
├── mock_data.sql              # Optional local DB seed
├── backend/
│   ├── .env.example          # Environment variable template
│   ├── database.py            # MySQL connection helper
│   ├── auth.py                # JWT token creation & verification, RBAC
│   ├── main.py                # FastAPI app entry point, router registration
│   ├── seed_live_data.py      # Seeds real restaurants from OpenStreetMap (optional)
│   ├── test_fetch.py          # DB connectivity test script
│   ├── models/
│   │   └── schemas.py         # (Pydantic schemas placeholder)
│   └── routes/
│       ├── users.py           # Signup, login, profile CRUD, user reviews/restaurants
│       ├── restaurants.py     # Restaurant CRUD, search, photo joins
│       ├── reviews.py         # Review CRUD for restaurants
│       ├── favorites.py       # Add/remove/list favourites (JWT)
│       ├── preferences.py     # User preference CRUD (for AI assistant)
│       ├── chat.py            # AI chatbot (Azure OpenAI + SQL)
│       ├── history.py         # User activity timeline
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

### AI Chatbot
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | Natural language query (Azure OpenAI + DB) |

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

- **Utkarsh Sharma (backend):** FastAPI REST API, MySQL (including Azure), JWT authentication, RBAC middleware, AI chatbot (Azure OpenAI), OpenStreetMap seeder, owner/admin workflows
- **Akash Kumar (frontend):** React UI with Vite + TailwindCSS, pages (Explore, Restaurant Detail, Auth, Profile, Preferences, Favourites, History, Owner Dashboard, Admin Panel), responsive design, API integration, AI UI, cuisine image fallbacks

---

## Architecture

```
┌─────────────────┐        ┌─────────────────────┐        ┌──────────────────┐
│   React (Vite)  │──API──▶│  FastAPI (Python)    │──SQL──▶│  MySQL           │
│   Port 5173     │        │  Port 8000           │        │  Local or Azure  │
│                 │        │                      │        └──────────────────┘
│  - TailwindCSS  │        │  - JWT Auth          │
│  - React Router │        │  - bcrypt            │        ┌──────────────────┐
│  - Axios        │        │  - Azure OpenAI      │──HTTP──▶│  Azure OpenAI    │
└─────────────────┘        └─────────────────────┘        └──────────────────┘
```
