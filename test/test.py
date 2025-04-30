import sys
import os
import unittest
from unittest.mock import patch, MagicMock, Mock
import json

# Add path to backend folder
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/backend")))
# Import the module
import VmachineCLI


class VendingMachineTests(unittest.TestCase):
    def setUp(self):
        # Patch out the DB reload so it always returns True and doesn't clear our storage
        self.reload_patcher = patch(
            "VmachineCLI.load_inventory_and_description_from_db",
            return_value=True
        )
        self.mock_reload = self.reload_patcher.start()
        self.addCleanup(self.reload_patcher.stop)

        # Patch pymysql.connect so no real DB calls happen
        self.connect_patcher = patch("VmachineCLI.pymysql.connect")
        self.mock_connect = self.connect_patcher.start()
        self.addCleanup(self.connect_patcher.stop)

        # Configure fake connection and cursor
        self.mock_conn = MagicMock()
        self.mock_cursor = MagicMock()
        self.mock_connect.return_value = self.mock_conn
        self.mock_conn.cursor.return_value = self.mock_cursor
        self.mock_cursor.__enter__.return_value = self.mock_cursor

        # Seed storage with four products
        VmachineCLI.storage = {
            "cola":        {"price": 1.00, "stock": 5},
            "lays chips": {"price": 1.50, "stock": 3},
            "water":       {"price": 1.25, "stock": 8},
            "chocolate":   {"price": 2.00, "stock": 1},
        }

        # Instantiate the machine
        self.machine = VmachineCLI.VendingMachine()
        self.machine.selected_product = None

    def test_imports(self):
        self.assertTrue(hasattr(VmachineCLI, "VendingMachine"))

    def test_basic_execution(self):
        products = self.machine.get_all_products()
        self.assertEqual(len(products), 4)
        self.assertIn("cola", products)
        self.assertIn("lays chips", products)
        self.assertIn("water", products)
        self.assertIn("chocolate", products)

    @patch("builtins.input", return_value="cola")
    def test_product_selection(self, mock_input):
        result = self.machine.select_product()
        self.assertTrue(result["success"])
        self.assertEqual(self.machine.selected_product, "cola")
        self.assertEqual(result["message"], "Selected product: cola")

    @patch("builtins.input", return_value="invalid_product")
    def test_product_selection_invalid(self, mock_input):
        result = self.machine.select_product()
        self.assertFalse(result["success"])
        self.assertIsNone(self.machine.selected_product)
        self.assertEqual(result["message"], "Product not found")

    def test_product_selection_api_mode(self):
        result = self.machine.select_product("cola")
        self.assertTrue(result["success"])
        self.assertEqual(self.machine.selected_product, "cola")
        self.assertEqual(result["message"], "Selected product: cola")

    @patch("VmachineCLI.process_payment")
    def test_successful_payment(self, mock_process_payment):
        mock_process_payment.return_value = {"success": True}
        self.machine.selected_product = "cola"
        initial_stock = VmachineCLI.storage["cola"]["stock"]

        result = self.machine.pay_for_product("test@example.com")

        self.assertTrue(result["success"])
        mock_process_payment.assert_called_once()
        # Stock in memory shouldn't change until finalize_transaction
        self.assertEqual(VmachineCLI.storage["cola"]["stock"], initial_stock)

    @patch("VmachineCLI.process_payment")
    def test_failed_payment(self, mock_process_payment):
        mock_process_payment.return_value = {"success": False}
        self.machine.selected_product = "cola"
        initial_stock = VmachineCLI.storage["cola"]["stock"]

        result = self.machine.pay_for_product("test@example.com")

        self.assertFalse(result["success"])
        self.assertIn("Payment failed", result["message"])
        self.assertEqual(VmachineCLI.storage["cola"]["stock"], initial_stock)
        self.assertEqual(self.machine.selected_product, "cola")

    def test_pay_without_selection(self):
        self.machine.selected_product = None
        result = self.machine.pay_for_product("test@example.com")
        self.assertFalse(result["success"])
        self.assertEqual(
            result["message"],
            "No product selected. Please select a product first."
        )

    def test_product_out_of_stock(self):
        VmachineCLI.storage["cola"]["stock"] = 0
        self.machine.selected_product = "cola"

        result = self.machine.pay_for_product("test@example.com")
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Product out of stock")

        # restore for other tests
        VmachineCLI.storage["cola"]["stock"] = 5

    def test_get_user_transactions(self):
        test_transactions = [
            {"item": "cola", "cost": 1.0},
            {"item": "chips", "cost": 1.5}
        ]
        # Configure cursor.fetchone to return JSON list and total_spent
        self.mock_cursor.fetchone.return_value = [
            json.dumps(test_transactions),
            2.5
        ]

        transactions, total_spent = self.machine.get_user_transactions(
            "test@example.com"
        )
        self.assertEqual(len(transactions), 2)
        self.assertEqual(transactions[0]["item"], "cola")
        self.assertEqual(transactions[1]["cost"], 1.5)
        self.assertEqual(total_spent, 2.5)

    def test_ensure_user_record_new_user(self):
        # Cursor.fetchone returns None → simulate no existing user
        self.mock_cursor.fetchone.return_value = None

        self.machine.ensure_user_record("new_user@example.com")
        # Should execute both SELECT and INSERT
        self.assertTrue(self.mock_cursor.execute.called)
        self.assertTrue(self.mock_conn.commit.called)

    def test_ensure_user_record_existing_user(self):
        # Cursor.fetchone returns a row → simulate existing user
        self.mock_cursor.fetchone.return_value = [1]

        self.machine.ensure_user_record("existing@example.com")
        # Should execute only the SELECT, but execute() is called at least once
        self.assertTrue(self.mock_cursor.execute.called)
        # No INSERT, but we aren’t checking commit here

    def test_store_transaction(self):
        # Cursor.fetchone returns an empty list → simulate first transaction
        self.mock_cursor.fetchone.return_value = ['[]']

        self.machine.store_transaction("test@example.com", "cola", 1.0)
        # Should execute SELECT and then UPDATE
        self.assertTrue(self.mock_cursor.execute.called)
        self.assertTrue(self.mock_conn.commit.called)


if __name__ == "__main__":
    unittest.main()
