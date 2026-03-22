# Yelp Prototype - Restaurant Discovery & Review Platform

A full-stack Yelp-style restaurant discovery and review platform with an AI-powered recommendation chatbot, built with React and FastAPI.

**Course:** DATA 236 | **Lab 1** | Spring 2026

---

## Tech Stack

### Backend
| Technology | Purpose |
|---|---|
| Python 3.9+ | Runtime |
| FastAPI | REST API framework |
| MySQL | Relational database |
| mysql-connector-python | Database driver |
| Pydantic | Request/response validation |
| bcrypt | Password hashing |
| PyJWT | JWT token authentication |
| LangChain + Ollama | Local AI chatbot (Llama 3.2) |

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
- **AI Assistant chatbot** - natural language restaurant search powered by Llama 3.2 (local, no API keys needed)

### Restaurant Owner Features
- **Owner dashboard** - analytics with total restaurants, reviews, average rating, and per-restaurant rating distribution
- **Manage restaurants** - edit restaurant details, upload photos
- **View reviews** - read-only view of reviews for owned restaurants
- **Submit new restaurants** - pending admin approval workflow

### Admin Features
- **Admin control panel** - approve/reject pending owner profiles and restaurant submissions
- **Assign/deassign** restaurant ownership

### AI Chatbot
The Explore page features an integrated **"Ask AI Assistant"** tab powered by LangChain and a local instance of **Llama 3.2 via Ollama**. Users can type natural language queries like:
- "I want cheap Mexican in SF"
- "Fancy Italian places"
- "Romantic dinner for two"

The AI extracts search filters (cuisine, price, city) and queries the database to return matching restaurants.

---

## Project Structure

```
yelp-prototype/
├── backend/
│   ├── .env.example          # Environment variable template
│   ├── database.py            # MySQL connection helper
│   ├── auth.py                # JWT token creation & verification, RBAC
│   ├── main.py                # FastAPI app entry point, router registration
│   ├── seed_live_data.py      # Seeds 500+ real restaurants from OpenStreetMap
│   ├── test_fetch.py          # DB connectivity test script
│   ├── models/
│   │   └── schemas.py         # (Pydantic schemas placeholder)
│   └── routes/
│       ├── users.py           # Signup, login, profile CRUD, user reviews/restaurants
│       ├── restaurants.py     # Restaurant CRUD, search, photo joins
│       ├── reviews.py         # Review CRUD for restaurants
│       ├── favorites.py       # Add/remove/list favourites
│       ├── preferences.py     # User preference CRUD (for AI assistant)
│       ├── chat.py            # AI chatbot endpoint (LangChain + Ollama)
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

Run these SQL statements to create the required tables:

```sql
CREATE DATABASE IF NOT EXISTS yelp_db;
USE yelp_db;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('user', 'owner', 'admin') DEFAULT 'user',
    is_approved BOOLEAN DEFAULT TRUE,
    phone VARCHAR(50),
    about_me TEXT,
    city VARCHAR(100),
    state VARCHAR(50),
    country VARCHAR(100),
    languages VARCHAR(255),
    gender VARCHAR(50),
    profile_picture VARCHAR(500),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE restaurants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    cuisine_type VARCHAR(100),
    description TEXT,
    address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    phone VARCHAR(50),
    email VARCHAR(255),
    website VARCHAR(500),
    hours_of_operation TEXT,
    pricing_tier VARCHAR(10),
    amenities TEXT,
    ambiance VARCHAR(100),
    average_rating DECIMAL(3,2) DEFAULT 0,
    review_count INT DEFAULT 0,
    owner_id INT,
    created_by INT,
    created_by_user_id INT,
    contact_info VARCHAR(255),
    price_tier VARCHAR(10),
    status ENUM('approved', 'pending', 'rejected') DEFAULT 'approved',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    restaurant_id INT NOT NULL,
    rating INT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT,
    review_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE
);

CREATE TABLE favorites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    restaurant_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE,
    UNIQUE KEY unique_fav (user_id, restaurant_id)
);

CREATE TABLE preferences (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    cuisine_preferences TEXT,
    price_range VARCHAR(20),
    preferred_locations TEXT,
    search_radius INT DEFAULT 10,
    dietary_needs TEXT,
    ambiance_preferences TEXT,
    sort_preference VARCHAR(50) DEFAULT 'Rating',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE restaurant_photos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    restaurant_id INT NOT NULL,
    photo_url VARCHAR(500) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (restaurant_id) REFERENCES restaurants(id) ON DELETE CASCADE
);

-- Insert default admin account (password: password123)
-- Generate hash with: python -c "import bcrypt; print(bcrypt.hashpw(b'password123', bcrypt.gensalt()).decode())"
INSERT INTO users (name, email, password_hash, role, is_approved) VALUES
('Admin', 'admin@example.com', '$2b$12$LJ3m4ys3Lk0TSwHCfJEMwOBaYKVqSp0K1NqOsGVT0DJiS0lFMfSG2', 'admin', TRUE);
```

---

## Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- MySQL 8.0+
- [Ollama](https://ollama.com/) (optional, for AI chatbot)

### 1. Clone the Repository
```bash
git clone https://github.com/Utkarshs9924/yelp-prototype.git
cd yelp-prototype
```

### 2. Set Up the Database
1. Start your MySQL server
2. Run the SQL schema above to create the `yelp_db` database and all tables

### 3. Set Up the Backend
```bash
cd backend

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# Install dependencies
pip install -r ../requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your MySQL credentials and JWT secret
```

### 4. Seed the Database (Optional)
Populate the database with 500+ real restaurants from OpenStreetMap:
```bash
cd backend
python seed_live_data.py
```

### 5. Start the Backend
```bash
cd backend
uvicorn main:app --reload --port 8000
```
The API will be available at `http://localhost:8000`. Swagger docs at `http://localhost:8000/docs`.

### 6. Set Up the Frontend
```bash
cd frontend
npm install
npm run dev
```
The frontend dev server runs at `http://localhost:5173` and proxies `/api` requests to the backend on port 8000.

### 7. Set Up AI Chatbot (Optional)
```bash
# Install Ollama from https://ollama.com
ollama pull llama3.2
ollama serve
```

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

### Reviews
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/restaurants/{id}/reviews` | Get reviews for a restaurant |
| POST | `/reviews` | Create a review |
| PUT | `/reviews/{id}` | Update a review |
| DELETE | `/reviews/{id}` | Delete a review |

### Favorites
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/favorites/{user_id}` | Get user's favorites |
| POST | `/favorites` | Add a favorite |
| DELETE | `/favorites/{id}` | Remove a favorite |

### Preferences (JWT Required)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/preferences` | Get current user's preferences |
| PUT | `/preferences` | Update/create preferences |

### AI Chatbot
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/chat` | Send natural language query |

### Owner (JWT + Owner/Admin Role)
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/owner/restaurants` | Get owner's restaurants |
| GET | `/owner/dashboard` | Get owner analytics |
| POST | `/owner/restaurants` | Submit new restaurant |
| GET | `/owner/restaurants/{id}/reviews` | Get reviews for owned restaurant |

### Admin (JWT + Admin Role)
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

> Note: You need to create these accounts via signup or insert them into the database manually.

---

## Team Contributions

- **Backend** (Utkarsh): FastAPI REST API, MySQL database design, JWT authentication, RBAC middleware, AI chatbot integration with LangChain + Ollama, OpenStreetMap data seeder, owner/admin workflows
- **Frontend** (Akash): React UI with Vite + TailwindCSS, all pages (Explore, Restaurant Detail, Auth, Profile, Preferences, Favourites, History, Owner Dashboard, Admin Panel), responsive design, API integration, AI chatbot widget, cuisine image fallback system

---

## Architecture

```
┌─────────────────┐        ┌─────────────────────┐        ┌──────────┐
│   React (Vite)  │──API──▶│  FastAPI (Python)    │──SQL──▶│  MySQL   │
│   Port 5173     │        │  Port 8000           │        │  Port 3306│
│                 │        │                      │        │          │
│  - TailwindCSS  │        │  - JWT Auth          │        │  Tables: │
│  - React Router │        │  - bcrypt            │        │  users   │
│  - Axios        │        │  - Pydantic          │        │  restaurants│
│  - React Icons  │        │  - LangChain+Ollama  │        │  reviews │
│                 │        │  - RBAC Middleware    │        │  favorites│
└─────────────────┘        └─────────────────────┘        │  preferences│
                                                           │  restaurant_photos│
                                                           └──────────┘
```
