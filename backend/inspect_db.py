from database import get_db_connection
import json

def inspect_schema():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    tables = ['users', 'reviews', 'restaurants', 'restaurant_photos', 'favourites', 'preferences']
    schema = {}
    
    for table in tables:
        try:
            cursor.execute(f"DESCRIBE {table}")
            schema[table] = cursor.fetchall()
        except Exception as e:
            schema[table] = str(e)
            
    conn.close()
    print(json.dumps(schema, indent=2, default=str))

if __name__ == "__main__":
    inspect_schema()
