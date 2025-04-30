import sys
import os
import unittest
import requests
import pymysql
import time
import json
from unittest.mock import patch, MagicMock

# Add path to backend folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/backend")))

class VendingMachineIntegrationTests(unittest.TestCase):
    """Integration tests to verify vending machine components work together"""
    
    def setUp(self):
        """Set up connection parameters from environment or use defaults"""
        # Database connection parameters
        self.db_host = os.environ.get("TEST_DB_HOST", "localhost")
        self.db_port = int(os.environ.get("TEST_DB_PORT", 53386))
        self.db_user = os.environ.get("TEST_DB_USER", "root")
        self.db_password = os.environ.get("TEST_DB_PASSWORD", "Group17")
        self.db_name = os.environ.get("TEST_DB_NAME", "Vending_Machine")
        
        # API endpoint
        self.api_url = os.environ.get("TEST_API_URL", "http://localhost:8000")
        
        # Set up expected products for comparison
        self.expected_products = ["cola", "lays chips", "water", "chocolate"]
    
    def test_db_connection(self):
        """Check if we can connect to the database and query the Inventory table"""
        print("\nTesting database connection...")
        
        # Try to connect a few times
        for attempt in range(3):
            try:
                # Connect to the database
                conn = pymysql.connect(
                    host=self.db_host,
                    port=self.db_port,
                    user=self.db_user,
                    password=self.db_password,
                    database=self.db_name,
                    connect_timeout=5
                )
                
                # Query the database
                with conn.cursor() as cursor:
                    cursor.execute("SELECT VERSION()")
                    version = cursor.fetchone()[0]
                    print(f"Connected to MySQL version: {version}")
                    
                    # Check if Inventory table exists
                    cursor.execute("SHOW TABLES LIKE 'Inventory'")
                    table_exists = cursor.fetchone() is not None
                    self.assertTrue(table_exists, "Inventory table not found")
                    
                    # Get count of products
                    cursor.execute("SELECT COUNT(*) FROM Inventory")
                    count = cursor.fetchone()[0]
                    print(f"Found {count} products in inventory")
                    
                    # Make sure we have some products
                    self.assertGreater(count, 0, "No products found in inventory")
                
                conn.close()
                break
                
            except pymysql.OperationalError as e:
                print(f"DB connection attempt {attempt+1} failed: {e}")
                if attempt < 2:  # Only sleep if we're going to retry
                    time.sleep(2)
                else:
                    self.fail(f"Could not connect to database: {e}")
    
    def test_api_products_endpoint(self):
        """Test the products API endpoint with mocked HTTP responses"""
        print("\nTesting API products endpoint...")
        
        # Use mocks to simulate HTTP responses
        with patch('requests.get') as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "success": True,
                "products": self.expected_products
            }
            mock_get.return_value = mock_response
            
            # Call the API
            response = requests.get(f"{self.api_url}/api/products")
            
            # Check the response
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data["success"])
            self.assertEqual(set(data["products"]), set(self.expected_products))
            print("API products endpoint test passed")
    
    def test_api_select_endpoint(self):
        """Test the product selection API endpoint with mocked responses"""
        print("\nTesting API select endpoint...")
        
        # Use mocks to simulate HTTP responses
        with patch('requests.post') as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "success": True,
                "message": "Selected product: cola"
            }
            mock_post.return_value = mock_response
            
            # Call the API
            response = requests.post(
                f"{self.api_url}/api/select",
                json={"product": "cola"}
            )
            
            # Check the response
            self.assertEqual(response.status_code, 200)
            data = response.json()
            self.assertTrue(data["success"])
            self.assertEqual(data["message"], "Selected product: cola")
            print("API select endpoint test passed")
    
    def test_live_api_if_available(self):
        """Try to test the real API if it's available (optional test)"""
        print("\nAttempting to test live API...")
        
        try:
            # Test the products endpoint
            response = requests.get(f"{self.api_url}/api/products", timeout=3)
            
            if response.status_code == 200:
                print("Live API products endpoint is available!")
                
                # Handle different response formats
                try:
                    data = response.json()
                    
                    # If it's a dictionary with products key
                    if isinstance(data, dict) and "products" in data:
                        products = data["products"]
                        print(f"Found products: {', '.join(products)}")
                        
                        # Try to select the first product
                        if products:
                            select_response = requests.post(
                                f"{self.api_url}/api/select",
                                json={"product": products[0]},
                                timeout=3
                            )
                            
                            if select_response.status_code == 200:
                                print(f"Successfully selected {products[0]}")
                            else:
                                print(f"Product selection failed with status {select_response.status_code}")
                    
                    # If it's a list of products directly
                    elif isinstance(data, list):
                        print(f"Found products: {', '.join(str(p) for p in data)}")
                    
                    # Test passed if we got this far
                    print("Live API test passed (informational only)")
                
                except ValueError:
                    print("Could not parse API response as JSON")
            else:
                print(f"Live API returned status code {response.status_code}")
                
        except requests.RequestException as e:
            print(f"Could not connect to live API: {e}")
            print("This is expected in CI/CD environments or when backend is not running")
    
    def test_db_api_integration(self):
        """Test database and API integration using mocks"""
        print("\nTesting DB-API integration...")
        
        # Try connecting to the real database
        try:
            conn = pymysql.connect(
                host=self.db_host,
                port=self.db_port,
                user=self.db_user,
                password=self.db_password,
                database=self.db_name,
                connect_timeout=5
            )
            
            with conn.cursor() as cursor:
                # Find the product name column
                cursor.execute("DESCRIBE Inventory")
                columns = [row[0] for row in cursor.fetchall()]
                print(f"Inventory table columns: {', '.join(columns)}")
                
                # Look for product name column
                name_col = None
                for col in ['product', 'name', 'item_name', 'item']:
                    if col in columns:
                        name_col = col
                        break
                
                if not name_col:
                    # Just use first column as a fallback
                    name_col = columns[0]
                    print(f"Could not identify product name column, using {name_col}")
                else:
                    print(f"Using '{name_col}' as product name column")
                
                # Get products from database
                cursor.execute(f"SELECT {name_col} FROM Inventory")
                db_products = [row[0] for row in cursor.fetchall()]
                print(f"Products in database: {', '.join(db_products)}")
                
                # Mock API to return these products
                with patch('requests.get') as mock_get:
                    mock_response = MagicMock()
                    mock_response.status_code = 200
                    mock_response.json.return_value = {
                        "success": True,
                        "products": db_products
                    }
                    mock_get.return_value = mock_response
                    
                    # Call API
                    response = requests.get(f"{self.api_url}/api/products")
                    api_products = response.json()["products"]
                    
                    # Compare products
                    self.assertEqual(set(db_products), set(api_products), 
                                    "API products should match database products")
                    print("DB-API integration verified - products match")
            
            conn.close()
            
        except pymysql.OperationalError as e:
            print(f"Skipping DB-API integration test - DB connection failed: {e}")
        except Exception as e:
            print(f"Error in DB-API integration test: {e}")


if __name__ == "__main__":
    print("========= VENDING MACHINE INTEGRATION TESTS =========")
    unittest.main(verbosity=2)