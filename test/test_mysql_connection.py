import os
import pymysql
import time
import sys

HOST = os.environ.get("MYSQL_HOST", "localhost")
PORT = int(os.environ.get("MYSQL_PORT", 53386))
# HOST = os.environ.get("DATABASE_HOST", "db8")
# PORT = int(os.environ.get("DATABASE_PORT", 3306))

def test_mysql_connection(max_attempts=2, delay=1):
    """Tries to connect to MySQL repeatedly until success or max_attempts reached."""
    for attempt in range(1, max_attempts + 1):
        try:
            connection = pymysql.connect(
                host=HOST,         
                port=PORT,            
                user="root",
                password="Group17",
                database="Vending_Machine"
            )
            with connection.cursor() as cursor:
                # Test connection by retrieving the MySQL version
                cursor.execute("SELECT VERSION()")
                version = cursor.fetchone()
                print(f"Connected to MySQL version: {version[0]}")
                
                # Run an additional SELECT query
                cursor.execute("SELECT * FROM Inventory;")
                rows = cursor.fetchall()
                print("Inventory table contents:")
                for row in rows:
                    print(row)
                    
            connection.close()
            return True
        except pymysql.err.OperationalError as e:
            print(f"Attempt {attempt}: MySQL not ready, retrying in {delay} seconds... ({e})")
            time.sleep(delay)
    return False

if __name__ == "__main__":
    if not test_mysql_connection():
        print("MySQL connection failed after multiple attempts.")
        sys.exit(1)
    else:
        print("MySQL connection succeeded.")
