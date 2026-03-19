# Yelp Prototype - Frontend

React-based frontend for the Yelp Prototype restaurant discovery platform.

## Tech Stack
- React 19 with Vite
- TailwindCSS for styling
- React Router for navigation
- Axios for API communication
- React Icons & React Hot Toast

## Getting Started

```bash
cd frontend
npm install
npm run dev
```

The dev server runs on http://localhost:5173 and proxies API calls to the backend on port 8000.

## Pages
- **Explore** - Search and browse restaurants
- **Restaurant Detail** - View restaurant info and reviews
- **Add Restaurant** - Create new restaurant listings
- **Login / Signup** - User authentication
- **Profile** - Edit user information
- **Preferences** - Set dining preferences for AI assistant
- **Favourites** - Saved restaurants
- **History** - Past reviews and activity
- **Owner Dashboard** - Restaurant analytics (owners)
- **Manage Restaurant** - Edit restaurant details (owners)
- **Owner Reviews** - View reviews for owned restaurants

## AI Chatbot
A floating chatbot widget appears on all pages for logged-in users, providing restaurant recommendations based on user preferences.
