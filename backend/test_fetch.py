import json
from datetime import datetime
from database import get_db_connection

def default_converter(o):
    if isinstance(o, datetime):
        return o.isoformat()
    raise TypeError(f"Object of type {o.__class__.__name__} is not JSON serializable")

def test_fetch():
    print("Connecting...")
    conn = get_db_connection()
    print("Connected. Fetching...")
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM restaurants")
    rows = cursor.fetchall()
    print(f"Fetched {len(rows)} rows.")
    conn.close()
    
    print("Attempting to serialize...")
    try:
        json_data = json.dumps(rows, default=default_converter)
        print(f"Successfully serialized! Length: {len(json_data)}")
    except Exception as e:
        print(f"JSON error: {e}")

if __name__ == '__main__':
    test_fetch()
