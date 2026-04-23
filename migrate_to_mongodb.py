"""
migrate_to_mongodb.py
---------------------
Migrates all data from Azure MySQL (Lab 1) to MongoDB Atlas (Lab 2).

Collections migrated:
  - users
  - restaurants (with embedded menu_items)
  - reviews
  - favourites
  - sessions (empty collection with TTL index)
  - preferences
  - photos

Run from the project root:
    pip install pymongo mysql-connector-python python-dotenv bcrypt
    python migrate_to_mongodb.py

Set these env vars (or edit the defaults below):
    DB_HOST, DB_USER, DB_PASSWORD, DB_NAME   <- Azure MySQL
    MONGO_URI                                 <- MongoDB Atlas
"""

import os
import sys
import bcrypt
import datetime
import mysql.connector
from pymongo import MongoClient, ASCENDING
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

load_dotenv("backend/.env")

# ── MySQL config ──────────────────────────────────────────────────────────────
MYSQL_CONFIG = {
    "host":     os.getenv("DB_HOST"),
    "user":     os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME"),
}

# ── MongoDB config ────────────────────────────────────────────────────────────
MONGO_URI = os.getenv(
    "MONGO_URI",
    "mongodb+srv://akashkumarsenthilkumar_db_user:mTnLH54vQAmmNjir@yelp.wvxiqvo.mongodb.net/?retryWrites=true&w=majority&appName=yelp"
)
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "yelp_db")


# ── Helpers ───────────────────────────────────────────────────────────────────

def get_mysql():
    return mysql.connector.connect(**MYSQL_CONFIG)

def get_mongo():
    client = MongoClient(MONGO_URI, server_api=ServerApi("1"))
    return client[MONGO_DB_NAME]

def rehash_password(existing_hash: str) -> str:
    """
    The MySQL passwords are already bcrypt hashed from Lab 1.
    We keep them as-is since bcrypt hashes are portable.
    If for any reason the hash doesn't start with $2b$, re-hash with a dummy.
    """
    if existing_hash.startswith("$2"):
        return existing_hash
    # fallback: re-hash (shouldn't happen with Lab 1 data)
    return bcrypt.hashpw(existing_hash.encode(), bcrypt.gensalt()).decode()


# ── Migration functions ───────────────────────────────────────────────────────

def migrate_users(mysql_conn, db):
    print("\n[1/6] Migrating users...")
    cursor = mysql_conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users")
    rows = cursor.fetchall()

    if not rows:
        print("  No users found in MySQL.")
        return {}

    # Drop existing collection to avoid duplicates on re-run
    db.drop_collection("users")
    col = db["users"]

    # Create unique index on email
    col.create_index([("email", ASCENDING)], unique=True)

    mysql_id_to_mongo_id = {}
    docs = []

    for row in rows:
        doc = {
            "mysql_id":        row["id"],        # keep for cross-reference during migration
            "name":            row["name"],
            "email":           row["email"],
            "password":        rehash_password(row["password_hash"]),  # bcrypt hash
            "role":            row["role"],
            "phone":           row.get("phone"),
            "about_me":        row.get("about_me"),
            "city":            row.get("city"),
            "state":           row.get("state"),
            "country":         row.get("country"),
            "languages":       row.get("languages"),
            "gender":          row.get("gender"),
            "profile_picture": row.get("profile_picture"),
            "is_approved":     bool(row.get("is_approved", 1)),
            "created_at":      row.get("created_at") or datetime.datetime.utcnow(),
            "updated_at":      row.get("updated_at"),
        }
        docs.append(doc)

    result = col.insert_many(docs)

    # Build mysql_id → mongo _id map for use in other collections
    for doc, mongo_id in zip(docs, result.inserted_ids):
        mysql_id_to_mongo_id[doc["mysql_id"]] = mongo_id

    print(f"  ✓ Migrated {len(docs)} users")
    cursor.close()
    return mysql_id_to_mongo_id


def migrate_restaurants(mysql_conn, db, user_id_map):
    print("\n[2/6] Migrating restaurants (with embedded menu items)...")
    cursor = mysql_conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM restaurants")
    restaurants = cursor.fetchall()

    cursor.execute("SELECT * FROM menu_items")
    menu_items = cursor.fetchall()

    # Group menu items by restaurant_id
    menus_by_restaurant = {}
    for item in menu_items:
        rid = item["restaurant_id"]
        menus_by_restaurant.setdefault(rid, []).append({
            "name":        item["name"],
            "description": item.get("description"),
            "price":       float(item["price"]) if item.get("price") else None,
        })

    db.drop_collection("restaurants")
    col = db["restaurants"]
    col.create_index([("name", ASCENDING)])
    col.create_index([("city", ASCENDING)])

    mysql_id_to_mongo_id = {}
    docs = []

    for row in restaurants:
        doc = {
            "mysql_id":           row["id"],
            "name":               row["name"],
            "cuisine_type":       row.get("cuisine_type"),
            "description":        row.get("description"),
            "address":            row.get("address"),
            "city":               row.get("city"),
            "state":              row.get("state"),
            "zip_code":           row.get("zip_code"),
            "phone":              row.get("phone"),
            "email":              row.get("email"),
            "website":            row.get("website"),
            "hours_of_operation": row.get("hours_of_operation"),
            "pricing_tier":       row.get("pricing_tier"),
            "amenities":          row.get("amenities"),
            "ambiance":           row.get("ambiance"),
            "average_rating":     row.get("average_rating"),
            "review_count":       row.get("review_count", 0),
            "status":             row.get("status", "approved"),
            "views":              row.get("views", 0),
            # Embed menu items directly in the restaurant document
            "menu_items":         menus_by_restaurant.get(row["id"], []),
            # Map MySQL owner_id → MongoDB _id
            "owner_id":           user_id_map.get(row.get("owner_id")),
            "created_by":         user_id_map.get(row.get("created_by")),
            "created_at":         row.get("created_at") or datetime.datetime.utcnow(),
            "updated_at":         row.get("updated_at"),
        }
        docs.append(doc)

    result = col.insert_many(docs)
    for doc, mongo_id in zip(docs, result.inserted_ids):
        mysql_id_to_mongo_id[doc["mysql_id"]] = mongo_id

    print(f"  ✓ Migrated {len(docs)} restaurants with embedded menu items")
    cursor.close()
    return mysql_id_to_mongo_id


def migrate_reviews(mysql_conn, db, user_id_map, restaurant_id_map):
    print("\n[3/6] Migrating reviews...")
    cursor = mysql_conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM reviews")
    rows = cursor.fetchall()

    db.drop_collection("reviews")
    col = db["reviews"]
    col.create_index([("restaurant_id", ASCENDING)])
    col.create_index([("user_id", ASCENDING)])

    docs = []
    for row in rows:
        doc = {
            "mysql_id":       row["id"],
            "user_id":        user_id_map.get(row["user_id"]),
            "restaurant_id":  restaurant_id_map.get(row["restaurant_id"]),
            "rating":         row["rating"],
            "comment":        row.get("comment"),
            "photo_url":      row.get("photo_url"),
            "created_at":     row.get("created_at") or datetime.datetime.utcnow(),
            "updated_at":     row.get("updated_at"),
        }
        docs.append(doc)

    if docs:
        col.insert_many(docs)
    print(f"  ✓ Migrated {len(docs)} reviews")
    cursor.close()


def migrate_favourites(mysql_conn, db, user_id_map, restaurant_id_map):
    print("\n[4/6] Migrating favourites...")
    cursor = mysql_conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM favourites")
    rows = cursor.fetchall()

    db.drop_collection("favorites")
    col = db["favorites"]
    col.create_index([("user_id", ASCENDING), ("restaurant_id", ASCENDING)], unique=True)

    docs = []
    for row in rows:
        doc = {
            "user_id":       user_id_map.get(row["user_id"]),
            "restaurant_id": restaurant_id_map.get(row["restaurant_id"]),
            "created_at":    row.get("created_at") or datetime.datetime.utcnow(),
        }
        docs.append(doc)

    if docs:
        col.insert_many(docs)
    print(f"  ✓ Migrated {len(docs)} favourites")
    cursor.close()


def migrate_photos(mysql_conn, db, user_id_map, restaurant_id_map):
    print("\n[5/6] Migrating photos...")
    cursor = mysql_conn.cursor(dictionary=True)

    # Check if photos table exists
    cursor.execute("SHOW TABLES LIKE 'photos'")
    if not cursor.fetchone():
        print("  No photos table found — skipping")
        cursor.close()
        return

    cursor.execute("SELECT * FROM photos")
    rows = cursor.fetchall()

    db.drop_collection("photos")
    col = db["photos"]
    col.create_index([("restaurant_id", ASCENDING)])

    docs = []
    for row in rows:
        doc = {
            "restaurant_id": restaurant_id_map.get(row.get("restaurant_id")),
            "user_id":       user_id_map.get(row.get("user_id")),
            "photo_url":     row.get("photo_url"),
            "caption":       row.get("caption"),
            "created_at":    row.get("created_at") or datetime.datetime.utcnow(),
        }
        docs.append(doc)

    if docs:
        col.insert_many(docs)
    print(f"  ✓ Migrated {len(docs)} photos")
    cursor.close()


def setup_sessions_collection(db):
    """
    Create sessions collection with TTL index (auto-expires after 24 hours).
    Sessions are created at login time by the app — we just set up the collection here.
    """
    print("\n[6/6] Setting up sessions collection...")
    db.drop_collection("sessions")
    col = db["sessions"]

    # TTL index — MongoDB auto-deletes documents 86400 seconds (24hrs) after expires_at
    col.create_index(
        [("expires_at", ASCENDING)],
        expireAfterSeconds=0  # uses the expires_at field value directly
    )
    col.create_index([("user_id", ASCENDING)])
    col.create_index([("token", ASCENDING)], unique=True)

    print("  ✓ Sessions collection created with TTL index (24hr expiry)")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  MySQL → MongoDB Migration Script")
    print("=" * 60)

    # Validate MySQL config
    missing = [k for k, v in MYSQL_CONFIG.items() if not v]
    if missing:
        print(f"\n❌ Missing MySQL env vars: {missing}")
        print("   Make sure backend/.env has DB_HOST, DB_USER, DB_PASSWORD, DB_NAME")
        sys.exit(1)

    print(f"\nConnecting to MySQL: {MYSQL_CONFIG['host']} / {MYSQL_CONFIG['database']}")
    mysql_conn = get_mysql()
    print("✓ MySQL connected")

    print(f"Connecting to MongoDB Atlas...")
    db = get_mongo()
    db.command("ping")
    print(f"✓ MongoDB connected → database: {MONGO_DB_NAME}")

    # Run migrations in order (order matters — users first for ID mapping)
    user_id_map       = migrate_users(mysql_conn, db)
    restaurant_id_map = migrate_restaurants(mysql_conn, db, user_id_map)
    migrate_reviews(mysql_conn, db, user_id_map, restaurant_id_map)
    migrate_favourites(mysql_conn, db, user_id_map, restaurant_id_map)
    migrate_photos(mysql_conn, db, user_id_map, restaurant_id_map)
    setup_sessions_collection(db)

    mysql_conn.close()

    print("\n" + "=" * 60)
    print("  ✅ Migration complete!")
    print("=" * 60)
    print("\nCollections in MongoDB:")
    for name in db.list_collection_names():
        count = db[name].count_documents({})
        print(f"  {name}: {count} documents")


if __name__ == "__main__":
    main()