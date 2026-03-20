# 🍽️ Yelp Prototype: The Ultimate AI-Powered Restaurant Discovery Platform

![Yelp Prototype Hero](https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?auto=format&fit=crop&w=1200&q=80)

Welcome to the **Yelp Prototype**, a dynamic, full-stack application designed to revolutionize how you find your next meal. This platform goes beyond traditional search filters by integrating a **100% offline, privacy-first Local AI Assistant** to deliver highly accurate, natural-language restaurant recommendations.

---

## ✨ Key Features

1. **Massive Real-Time Database** 🌍
   Dynamically fetches and seeds 500+ real-world restaurants from across the San Francisco Bay Area using the OpenStreetMap (Overpass) API. No fake data—just real places you can visit today.

2. **Smart Cuisine Imagery** 📸
   Implements an intelligent cuisine-mapping algorithm that tags seeded restaurants with high-quality, culturally relevant photos from Unsplash. A Mexican joint gets beautiful taco photos; a Pizzeria gets artisan slices.

3. **Privacy-First Local AI Assistant** 🤖
   Say goodbye to paid API keys and cloud privacy concerns. The Explore page features an integrated **"Ask AI Assistant"** tab powered by LangChain and a localized instances of **Llama 3.2 (via Ollama)**. Just ask, *"I want cheap Mexican in SF"*, and the AI will handle the rest—parsing intent and querying the SQL database intelligently.

4. **Responsive Modern UI** 💻
   Built with Vite + React and styled heavily with Tailwind CSS. The app features a beautiful Hero section, smooth animations (`animate-fade-in`), intelligent fallback images, and responsive grids for seamless browsing on any device.

---

## 🛠️ Architecture & Tech Stack

This project uses a decoupled Frontend/Backend architecture for massive scalability.

- **Frontend:** React 18, Vite, Tailwind CSS, React-Router-Dom, Axios
- **Backend:** Python 3.9+, FastAPI, Uvicorn, LangChain (Community)
- **Local AI Engine:** Ollama (Llama 3.2:latest)
- **Database:** MySQL
- **Data Sourcing:** OpenStreetMap Overpass API

---

## 🚀 How We Tackled The Challenges

### Problem 1: Generic Mock Images
**Challenge:** Early iterations strictly bound every restaurant to a single 800x600 gray placeholder.
**Solution:** We built a custom python seeder (`seed_live_data.py`) with a `CUISINE_IMAGE_MAP` dictionary. It parses the OSM `cuisine` tags via RegEx matching and fetches distinctly contextual images from a curated Unsplash hash-list.

### Problem 2: API Costs & AI Privacy
**Challenge:** The user requested an advanced "Search by intent" (Natural Language Processing) chatbot, but didn't want to expose data to OpenAI or pay for costly GPT-4 tokens.
**Solution:** We replaced the conventional OpenAI integration with a fully local, open-weights architecture using **Ollama**. The FastAPI backend implements a zero-temperature `ChatOllama` chain that executes 100% locally on the user's hardware.

### Problem 3: Handling 500+ Seeding Requests cleanly
**Challenge:** Scraping 500+ locations from the Bay Area Overpass endpoint caused query timeouts.
**Solution:** We optimized the OSM bounding box coordinates (`(37.3,-122.5,38.0,-121.9)`) and specifically targeted the `node["amenity"="restaurant"]` filter to massively dramatically decrease DB load, while utilizing `GROUP_CONCAT` in MySQL for rapid 1-to-N photo retrieval.

---

## 🚦 Local Setup Instructions

### 1. Database
Ensure your MySQL server is running locally.

### 2. Backend
Navigate to the `/backend` directory:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
Copy `.env.example` to `.env` and fill in your DB credentials. Run the seeder, then run the engine:
```bash
python seed_live_data.py
uvicorn main:app --reload --port 8000
```

### 3. Frontend
Navigate to the `/frontend` directory:
```bash
npm install
npm run dev
```

### 4. Local AI Setup
If you want to use the AI Search tab, download [Ollama](https://ollama.com/) and pull the lightweight Llama 3.2 model:
```bash
ollama run llama3.2
```
Leave the instance running in the background.

---

*For queries, issues, or contributions, please refer to our repository guidelines or open a comprehensive pull request!*
