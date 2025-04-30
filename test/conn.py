from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError

# TODO local host does not work when running through docker
connection_string = "mysql+pymysql://root:Group17@localhost:53386/Vending_Machine"

try:
    engine = create_engine(connection_string)
    connection = engine.connect()
    connection.close()
    print("Connection successful!")
except OperationalError as e:
    print(f"Connection failed: {e}")

# Test to help with debugging with connection issues
with engine.connect() as conn: 

    # TODO Name of column changed from name to item_name
    result = conn.execute(text("""
                    SELECT item_name FROM Inventory WHERE item_name = :product_name 
                """), {"product_name": "coke"})
    
    # Prints out what looks like a reference
    print(result)


    # THIS WORKS, but is in json format
    rows = [row._asdict() for row in result]
    print(rows)

    # Use this
    rows = [row[0] for row in result]
    print(rows)

