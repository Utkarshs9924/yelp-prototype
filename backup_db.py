import os
import mysql.connector
from dotenv import load_dotenv

def backup_db():
    load_dotenv('backend/.env')
    
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DB_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'yelp_db')
        )
        cursor = conn.cursor(dictionary=True)
        
        # Get all tables
        cursor.execute("SHOW TABLES")
        tables = [list(row.values())[0] for row in cursor.fetchall()]
        
        backup_file = 'yelp_db_backup.sql'
        with open(backup_file, 'w') as f:
            for table in tables:
                print(f"Backing up table: {table}")
                # Write CREATE TABLE
                cursor.execute(f"SHOW CREATE TABLE {table}")
                create_stmt = cursor.fetchone()['Create Table']
                f.write(f"\nDROP TABLE IF EXISTS `{table}`;\n")
                f.write(f"{create_stmt};\n\n")
                
                # Write INSERT DATA
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                if rows:
                    for row in rows:
                        columns = ", ".join([f"`{k}`" for k in row.keys()])
                        values = []
                        for val in row.values():
                            if val is None:
                                values.append("NULL")
                            elif isinstance(val, (int, float)):
                                values.append(str(val))
                            else:
                                escaped_val = str(val).replace("'", "''").replace("\\", "\\\\")
                                values.append(f"'{escaped_val}'")
                        f.write(f"INSERT INTO `{table}` ({columns}) VALUES ({', '.join(values)});\n")
        
        print(f"✅ Backup complete: {backup_file}")
        
    except Exception as e:
        print(f"❌ Backup failed: {e}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    backup_db()
