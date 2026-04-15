#!/usr/bin/env python3
"""Test MongoDB Atlas connection"""
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# MongoDB connection string
MONGO_URI = "mongodb+srv://akashkumarsenthilkumar_db_user:mTnLH54vQAmmNjir@yelp.wvxiqvo.mongodb.net/?retryWrites=true&w=majority&appName=yelp"

def test_connection():
    try:
        # Create a new client and connect to the server
        client = MongoClient(MONGO_URI, server_api=ServerApi('1'))
        
        # Send a ping to confirm a successful connection
        client.admin.command('ping')
        print("✅ Successfully connected to MongoDB Atlas!")
        
        # List databases
        db_list = client.list_database_names()
        print(f"\n📊 Available databases: {db_list}")
        
        # Create/access yelp_db
        db = client['yelp_db']
        print(f"\n✅ Created/accessed 'yelp_db' database")
        
        # Test collections
        collections = ['users', 'restaurants', 'reviews', 'favorites', 'sessions']
        for coll in collections:
            db[coll].insert_one({'test': True})
            db[coll].delete_one({'test': True})
            print(f"  ✓ Collection '{coll}' is ready")
        
        print(f"\n🎉 MongoDB setup complete!")
        
        client.close()
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")
        return False

if __name__ == "__main__":
    test_connection()
