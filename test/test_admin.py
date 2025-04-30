#!/usr/bin/env python
import os, sys
import django

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/backend")))

#  we are using django's settings, use test_settings we created
os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "vending_api.test_settings"
)

# this entire set of code is to avoid DB calls
import VmachineCLI
class _NoOpVM:
    def __init__(self, *args, **kwargs):
        # do nothing (no DB calls)
        pass
# Replace the real class with our no‐op
VmachineCLI.VendingMachine = _NoOpVM # this avoids running db8
# Populate Django
django.setup()

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from unittest.mock import patch, MagicMock
import json


class AdminViewsTests(APITestCase):
    def setUp(self):
        self.client         = APIClient()
        # reverse creates urls
        self.inventory_url  = reverse('update-inventory')
        self.price_url      = reverse('update-price')
        self.threshold_url  = reverse('update-threshold')

        reload_patcher = patch(
            "api.admin_views.load_inventory_and_description_from_db",
            return_value=True
        )
        self.mock_reload = reload_patcher.start()
        self.addCleanup(reload_patcher.stop)

    @patch('api.admin_views.get_engine')
    def test_update_inventory_success(self, mock_get_engine):
        # update inventory - success
        mock_engine = MagicMock()
        mock_conn   = MagicMock()
        mock_engine.begin.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        mock_conn.execute.return_value = MagicMock()

        resp = self.client.post(
            self.inventory_url,
            {'product_name': 'cola', 'quantity': 10},
            format='json'
        )

        # verify
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(mock_conn.execute.call_count, 2)
        self.assertIn('Changed inventory of cola', resp.data)

    def test_update_inventory_invalid_payload(self):
        # update inventory - invalid
        resp = self.client.post(
            self.inventory_url,
            {},
            format='json'
        )
        # verify
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('product_name', resp.data)
        self.assertIn('quantity',     resp.data)

    @patch('api.admin_views.get_engine')
    def test_update_inventory_product_not_found(self, mock_get_engine):
        # update - not found
        mock_engine = MagicMock()
        mock_conn   = MagicMock()
        mock_engine.begin.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        mock_conn.execute.return_value = None

        resp = self.client.post(
            self.inventory_url,
            {'product_name': 'does_not_exist', 'quantity': 5},
            format='json'
        )

        # verify
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data['error'], 'Failed to fetch products')

    @patch('api.admin_views.get_engine')
    def test_update_price_success(self, mock_get_engine):
        # price - success
        mock_engine = MagicMock()
        mock_conn   = MagicMock()
        mock_engine.begin.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        mock_conn.execute.return_value = MagicMock()

        resp = self.client.post(
            self.price_url,
            {'product_name': 'cola', 'price': 2.50},
            format='json'
        )

        # verify
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(mock_conn.execute.call_count, 2)
        self.assertIn('Changed price of cola', resp.data)

    def test_update_price_invalid_payload(self):
        # price - invalid payload
        resp = self.client.post(
            self.price_url,
            {},
            format='json'
        )
        # verify
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('product_name', resp.data)
        self.assertIn('price',        resp.data)

    @patch('api.admin_views.get_engine')
    def test_update_price_product_not_found(self, mock_get_engine):
        # update price  - product not found
        mock_engine = MagicMock()
        mock_conn   = MagicMock()
        mock_engine.begin.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        mock_conn.execute.return_value = None

        resp = self.client.post(
            self.price_url,
            {'product_name': 'nope', 'price': 1.23},
            format='json'
        )

        # verify
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data['error'], 'Failed to fetch products')

    @patch('api.admin_views.get_engine')
    def test_update_threshold_success(self, mock_get_engine):
        # threshold check - success
        mock_engine = MagicMock()
        mock_conn   = MagicMock()
        mock_engine.begin.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        mock_conn.execute.return_value = MagicMock()

        resp = self.client.post(
            self.threshold_url,
            {'product_name': 'cola', 'threshold': 3},
            format='json'
        )

        # verify
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(mock_conn.execute.call_count, 2)
        self.assertIn('Changed threshold of cola', resp.data)

    def test_update_threshold_invalid_payload(self):
        # threshold check - invalid payload
        resp = self.client.post(
            self.threshold_url,
            {},
            format='json'
        )
        # verify
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('product_name', resp.data)
        self.assertIn('threshold',    resp.data)

    @patch('api.admin_views.get_engine')
    def test_update_threshold_product_not_found(self, mock_get_engine):
        # threshold check - product not found
        mock_engine = MagicMock()
        mock_conn   = MagicMock()
        mock_engine.begin.return_value.__enter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        mock_conn.execute.return_value = None

        resp = self.client.post(
            self.threshold_url,
            {'product_name': 'no-such-item', 'threshold': 5},
            format='json'
        )

        # verify
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(resp.data['error'], 'Failed to fetch products')


if __name__ == '__main__':
    import unittest
    unittest.main()