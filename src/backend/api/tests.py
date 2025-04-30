
from django.test import TestCase
from rest_framework.test import APIClient
from VmachineCLI import VendingMachine


class VendingMachineAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.vm = VendingMachine()

    def test_get_all_products(self):
        response = self.client.get("/api/products/")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)

    def test_select_product_success(self):
        payload = {"product_name": "Pepsi"}
        response = self.client.post("/api/select-product/", payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.data)

    def test_select_invalid_product(self):
        payload = {"product_name": "InvalidItem"}
        response = self.client.post("/api/select-product/", payload, format="json")
        self.assertEqual(response.status_code, 400)

    def test_payment_success(self):
        self.vm.select_product("Pepsi")
        payload = {"user_email": "test@example.com"}
        response = self.client.post("/api/pay/", payload, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("success", response.data)

    def test_current_selection(self):
        self.vm.select_product("Pepsi")
        response = self.client.get("/api/current-selection/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["selected_product"]["name"], "Pepsi")
