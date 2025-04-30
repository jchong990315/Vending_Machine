from payments import process_payment
from decimal import Decimal
import os
import pymysql
import time
import sys
import json

# Global storage dictionary
storage = {}

# Database connection settings
HOST = os.environ.get("DATABASE_HOST", "db8")
PORT = int(os.environ.get("DATABASE_PORT", 3306))


def normalize_item_name(name):
    """Used to make sure the name in storage can be turned to lowercase when doing user
       input matching.
    """
    return name.strip().lower()


def load_inventory_and_description_from_db(max_attempts=5, delay=2):
    """
    Tries to connect to MySQL repeatedly until success or max_attempts reached.
    Loads inventory data into the global storage dictionary.
    """
    global storage  # # noqa: F824

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

                # Run a SELECT query on the Inventory table
                cursor.execute("SELECT * FROM Inventory;")
                rows = cursor.fetchall()

                # Fetch Item Description data
                cursor.execute("SELECT i_id, description, calories, carbohydrates, allergy_info FROM Item_Description;")
                description_rows = cursor.fetchall()

                # Clear existing storage
                storage.clear()

                # Reformat fetched data into the desired dictionary format
                for row in rows:
                    key = normalize_item_name(row[1])
                    storage[key] = {
                        "i_id": row[0],
                        "price": row[3],
                        "stock": row[2],
                        "channel": row[5],
                        "description": None,
                        "calories": None,
                        "carbohydrates": None,
                        "allergy_info": None
                    }

                # Create a dictionary for item descriptions based on i_id for easier matching
                descriptions_dict = {desc_row[0]: {
                    "description": desc_row[1],
                    "calories": desc_row[2],
                    "carbohydrates": desc_row[3],
                    "allergy_info": desc_row[4]
                } for desc_row in description_rows}

                # Now loop through storage and populate description fields from descriptions_dict
                for product_name, details in storage.items():
                    # Check if the product's i_id has a corresponding entry in the descriptions_dict

                    item_description = descriptions_dict.get(details["i_id"])
                    if item_description:
                        details["description"] = item_description["description"]
                        details["calories"] = item_description["calories"]
                        details["carbohydrates"] = item_description["carbohydrates"]
                        details["allergy_info"] = item_description["allergy_info"]
                        print(f"Updated {product_name} with description: {details['description']}")

                print("Formatted inventory:")
                print(storage)

            connection.close()
            return True
        except pymysql.err.OperationalError as e:
            print(f"Attempt {attempt}: MySQL not ready, retrying in {delay} seconds... ({e})")
            time.sleep(delay)
    return False


def test_revert_stock(product_name):
    """
    For testing purposes, adds 1 to the product's stock in MySQL,
    then prints a success message if the update is successful.
    """
    normalized_name = normalize_item_name(product_name)
    try:
        connection = pymysql.connect(
            host=HOST,
            port=PORT,
            user="root",
            password="Group17",
            database="Vending_Machine"
        )
        with connection.cursor() as cursor:
            query = "UPDATE Inventory SET stock = stock + 1 WHERE LOWER(item_name) = %s;"
            cursor.execute(query, (normalized_name,))
        connection.commit()
        connection.close()
        print("Successfully test: Added 1 back to", product_name)
    except Exception as e:
        print("Error in test_revert_stock:", e)


class VendingMachine:
    def __init__(self):
        # First make sure load inventory is done
        if not storage:
            if not load_inventory_and_description_from_db():
                print("Failed to load inventory from the database. Exiting.")
                sys.exit(1)
        self.selected_product = None

    def get_all_products(self):
        # Ensure storage is populated before returning products.
        if not storage:
            print("Inventory empty, loading from database...")
            if not load_inventory_and_description_from_db():
                print("Failed to load inventory from the database.")
                return {}
        
        # Reload inventory to ensure we have latest data
        if not load_inventory_and_description_from_db():
            print("Failed to reload inventory")
            return {}
            
        products = {}
        for name, details in storage.items():
            products[name] = {
                "price": details.get("price", 0.0),
                "stock": details.get("stock", 0),
                "available": details.get("stock", 0) > 0,
                "description": details.get("description", "No description available."),
                "calories": details.get("calories", 0),
                "carbohydrates": details.get("carbohydrates", 0),
                "allergy_info": details.get("allergy_info", "No allergy info available."),
            }
        return products

    def print_products(self):
        products = self.get_all_products()
        for name, info in products.items():
            availability = "In Stock" if info["stock"] > 0 else "Out of Stock"
            print(f"{name.title()} - ${info['price']:.2f} - {availability}")

    def select_product(self, product_name=None):
        """
        Select a product by name
        If product_name is None, prompt for input (CLI mode)
        Otherwise, use the provided name (API mode)
        """
        if product_name is None:
            # CLI mode
            product_name = input("Enter the product name: ").lower()
            print(product_name)

        # Reload inventory to ensure we have latest stock
        if not load_inventory_and_description_from_db():
            return {"success": False, "message": "Failed to load inventory"}

        if product_name.lower() in storage:
            # Check if product is in stock
            if storage[product_name.lower()]["stock"] <= 0:
                return {"success": False, "message": "Product out of stock"}
            self.selected_product = product_name.lower()
            return {"success": True, "message": f"Selected product: {product_name}"}
        else:
            return {"success": False, "message": "Product not found"}

    # Comes before pay_for_product as we need to use this there
    def store_transaction(self, email, product, cost):
        try:
            connection = pymysql.connect(
                host=HOST,
                port=PORT,
                user="root",
                password="Group17",
                database="Vending_Machine"
            )
            with connection.cursor() as cursor:
                get_transaction_query = "SELECT transactions FROM UserProfile WHERE email = %s;"
                cursor.execute(get_transaction_query, (email,))
                # It only has one lsit so fetchone will work
                result = cursor.fetchone()
                if result:
                    # Get the string from our list
                    transaction_as_string = result[0]
                    try:
                        transactions = json.loads(transaction_as_string)
                    except Exception:
                        transactions = []
                else:
                    # Empty transaction list, need to append first transaction
                    transactions = []

                # Append new transaction - for now we store product and cost
                transactions.append({"item": product, "cost": float(cost)})

                # We are keeping only the latest 5 transactions
                if len(transactions) > 5:
                    transactions = transactions[-5:]

                # Update the record with the new transactions list
                transactions_updated = json.dumps(transactions)
                update_query = "UPDATE UserProfile SET transactions = %s WHERE email = %s;"
                cursor.execute(update_query, (transactions_updated, email))
                connection.commit()
        except Exception as e:
            print("Error updating user transactions:", e)
        finally:
            if connection:
                connection.close()

    def pay_for_product(self, user_email=None):
        """
        Process payment for selected product
        If user_email is None, prompt for input (CLI mode)
        Otherwise, use the provided email (API mode)
        """
        if not hasattr(self, 'selected_product') or self.selected_product is None:
            return {"success": False,
                    "message": "No product selected. Please select a product first."}

        product_name = self.selected_product
        print("product_name:", product_name)
        if user_email is None:
            # CLI mode
            user_email = input("Enter your email for the receipt: ")

        # Reload inventory to ensure we have latest stock
        if not load_inventory_and_description_from_db():
            return {"success": False, "message": "Failed to load inventory"}

        if product_name in storage:
            # Check if product is in stock
            if storage[product_name]["stock"] <= 0:
                return {"success": False, "message": "Product out of stock"}

            amount = int(Decimal(storage[product_name]["price"]) * 100)  # Convert amount to cents for Stripe
            print("amount:", amount)
            payment_result = process_payment(product_name, amount, user_email)

            # Check if the payment was initiated successfully
            if payment_result.get("success"):
                return {
                    "success": True,
                    "message": f"Payment initiated for {product_name.title()}.",
                    "client_secret": payment_result.get("paymentIntent", {}).get("client_secret")
                }

            else:
                return {"success": False, "message": f"Payment failed: {payment_result}"}
        else:
            return {"success": False, "message": "Invalid product selection"}

    def get_user_transactions(self, email):
        """
        Retrieve the transactions for a given user from the database.
        Returns a list of transactions.
        """
        connection = pymysql.connect(
            host=HOST,
            port=PORT,
            user="root",
            password="Group17",
            database="Vending_Machine"
        )
        with connection.cursor() as cursor:
            query = "SELECT transactions, total_spent FROM UserProfile WHERE email = %s;"
            cursor.execute(query, (email,))
            result = cursor.fetchone()
        connection.close()

        if result:
            transactions_str = result[0] or "[]"
            try:
                transactions = json.loads(transactions_str)
            except Exception:
                transactions = []
            total_spent = result[1]
        else:
            transactions = []
            total_spent = 0.00
        print(transactions)
        return transactions, total_spent

    def finalize_transaction(self, user_email):
        """
        Finalize a successful payment by:
        - Deducting stock in the Inventory table.
        - Retrieving necessary inventory details.
        - Retrieving the user id from the UserProfile table.
        - Inserting a new record in the Transactions table.
        - Inserting a corresponding record in the transactions_items table.
        - Deducting stock in the in-memory storage.
        - Updating the user's transactions JSON via store_transaction.
        - Clearing the selected product.
        """
        product_name = self.selected_product
        print("self.selected_product:", product_name)
        if product_name not in storage:
            return {"success": False, "message": "Invalid product selection."}

        # Update stock in the database
        try:
            connection = pymysql.connect(
                host=HOST,
                port=PORT,
                user="root",
                password="Group17",
                database="Vending_Machine"
            )
            with connection.cursor() as cursor:
                update_stock_query = "UPDATE Inventory SET stock = stock - 1 WHERE LOWER(item_name) = %s AND stock > 0;"
                cursor.execute(update_stock_query, (product_name,))
                if cursor.rowcount == 0:
                    raise Exception("Out of stock or error updating inventory.")

                # 2. Retrieve inventory details: i_id and price.
                select_inventory_query = """
                    SELECT i_id, price FROM Inventory
                    WHERE LOWER(item_name) = %s;
                """
                cursor.execute(select_inventory_query, (product_name,))
                row = cursor.fetchone()
                if not row:
                    raise Exception("Product not found in inventory.")
                i_id, price = row[0], row[1]

                # 3. Retrieve the user's id from the UserProfile table.
                user_query = "SELECT id FROM UserProfile WHERE email = %s;"
                cursor.execute(user_query, (user_email,))
                user_row = cursor.fetchone()
                if not user_row:
                    raise Exception("User record not found.")
                user_id = user_row[0]

                # 4. Insert a new record into the Transactions table.
                insert_trans_query = """
                    INSERT INTO Transactions (user_id, transaction_date, total, payment_id, payment_status)
                    VALUES (%s, NOW(), %s, %s, %s);
                """
                dummy_payment_id = "dummy_payment"  # Replace with actual payment id if available.
                payment_status = "completed"
                cursor.execute(insert_trans_query, (user_id, price, dummy_payment_id, payment_status))
                t_id = cursor.lastrowid  # Retrieve the auto-generated transaction ID.

                # 5. Insert a record into the transactions_items table.
                insert_item_query = """
                    INSERT INTO transactions_items (t_id, i_id, item_name, quantity, price)
                    VALUES (%s, %s, %s, %s, %s);
                """
                quantity = 1  # Adjust the quantity if your design allows for multiples.
                cursor.execute(insert_item_query, (t_id, i_id, product_name, quantity, price))

                # Commit the entire transaction.
                connection.commit()
        except Exception as e:
            connection.rollback()
            return {"success": False, "message": f"Error finalizing transaction: {e}"}
        finally:
            connection.close()

        # 6. Deduct stock in in-memory storage.
        storage[product_name]["stock"] -= 1

        # store product cost
        product_cost = storage[product_name]["price"]

        # Store the transaction
        self.store_transaction(user_email, product_name, storage[product_name]["price"])

        # update total_spent as well
        try:
            connection = pymysql.connect(
                host=HOST,
                port=PORT,
                user="root",
                password="Group17",
                database="Vending_Machine"
            )
            with connection.cursor() as cursor:
                update_query = "UPDATE UserProfile SET total_spent = total_spent + %s WHERE email = %s;"
                cursor.execute(update_query, (product_cost, user_email))
            connection.commit()
        except Exception as e:
            print("Error updating total spent:", e)
        finally:
            if connection:
                connection.close()

        # Clear the selected product
        prev_product = self.selected_product
        self.selected_product = None

        return {"success": True, "message": f"Payment successful! Dispensing {prev_product.title()}"}

    # CLI method - keep this for CLI usage
    def start(self):
        print("Hi I am T17 Vending Machine - What can I dispense for you today?")
        KICK_RESPONSES = [
            "Ouch! That hurts!",
            "Hey! Careful with that!",
            "*Clang* — you really kicked me, huh?",
            "I'm just a machine — why you gotta be violent?"
        ]
        while True:
            print("1. Display all products")
            print("2. Select a product")
            print("3. Pay for product(s)")
            print("4. Kick the machine")
            print("5. Exit")

            try:
                user_choice = int(input("Please make a selection: "))

                if user_choice == 1:
                    self.print_products()
                elif user_choice == 2:
                    result = self.select_product()
                    print(result["message"])
                elif user_choice == 3:
                    result = self.pay_for_product()
                    print(result["message"])
                elif user_choice == 4:
                    import random
                    print(random.choice(KICK_RESPONSES))
                elif user_choice == 5:
                    print("Thank you, come again!")
                    break
                else:
                    print("Command not found, try again")
            except ValueError:
                print("Please enter a valid number")

    # Create a new user record if user is new
    # New method to ensure a user record exists
    def ensure_user_record(self, email):
        """
        Check if a user record exists in the UserProfile table.
        If not, create a new record.
        """
        try:
            connection = pymysql.connect(
                        host=HOST,
                        port=PORT,
                        user="root",
                        password="Group17",
                        database="Vending_Machine"
            )
            with connection.cursor() as cursor:
                user_exists = "SELECT id FROM UserProfile WHERE email = %s;"
                cursor.execute(user_exists, (email,))
                result = cursor.fetchone()
                if result is None:
                    # New user so create a record
                    insert_query = """
                        INSERT INTO UserProfile (email, transactions)
                        VALUES (%s, %s);
                    """
                    cursor.execute(insert_query, (email, '[]'))
                    connection.commit()
                    print(f"Created new user record for {email}")
                else:
                    print(f"User record already exists for {email}")
        except Exception as e:
            print("Error in ensure_user_record:", e)
        finally:
            if connection:
                connection.close()


# This ensures the CLI only runs when this file is executed directly
if __name__ == '__main__':
    # Create the instance
    machine1 = VendingMachine()
    # Run the CLI
    machine1.start()
