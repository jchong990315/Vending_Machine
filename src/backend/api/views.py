import os
import sys
# from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

# Get the directory two levels up from the current file
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)

# Import VendingMachine class
from VmachineCLI import VendingMachine

from .serializers import ProductSerializer, ProductSelectionSerializer, PaymentSerializer

# Create a VendingMachine instance (singleton pattern)
vending_machine = VendingMachine()


class ProductListView(APIView):
    """API view for listing all vending machine products"""

    def get(self, request):
        """Get all products with their information"""
        products_dict = vending_machine.get_all_products()

        # Convert the dict to a list of objects with 'name' included
        products_list = [
            {
                "name": name,
                "price": info["price"],
                "stock": info["stock"],
                "available": info["stock"] > 0,
                "description": info["description"],
                "calories": info["calories"],
                "carbohydrates": info["carbohydrates"],
                "allergy_info": info["allergy_info"],
                "channel": info.get("channel", "A1")  # Add channel field with default value
            }
            for name, info in products_dict.items()
        ]

        # Log the products list to check the structure before passing it to the serializer
        print("Products List to be serialized:", products_list)
        #
        #   "diet coke": {"price": 2.50, "stock": 100, "available": true},
        #   "sprite": {"price": 2.50, "stock": 50, "available": true}
        #
        #   {"name": "diet coke", "price": 2.50, "stock": 100, "available": true},
        #   {"name": "sprite", "price": 2.50, "stock": 50, "available": true}
        #
        #
        serializer = ProductSerializer(products_list, many=True)
        # Log the data to check the content
        print("Serialized Products:", serializer.data)
        return Response(serializer.data)


class ProductSelectionView(APIView):
    """API view for selecting a product"""

    def post(self, request):
        """Select a product for purchase"""
        serializer = ProductSelectionSerializer(data=request.data)

        if serializer.is_valid():
            result = vending_machine.select_product(serializer.validated_data['product_name'])

            if result['success']:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentView(APIView):
    """API view for processing payment"""

    def post(self, request):
        """Process payment for selected product"""
        serializer = PaymentSerializer(data=request.data)

        if serializer.is_valid():
            result = vending_machine.pay_for_product(serializer.validated_data['user_email'])

            if result['success']:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CurrentSelectionView(APIView):
    """API view for checking currently selected product"""

    def get(self, request):
        """Get the currently selected product"""
        if hasattr(vending_machine, 'selected_product') and vending_machine.selected_product:
            return Response({
                "selected_product": vending_machine.selected_product
            })
        else:
            return Response({
                "selected_product": None
            })


class UserProfileView(APIView):
    """
    API view to ensure that a UserProfile exists for the authenticated user.
    """
    def post(self, request):
        user_email = request.headers.get('X-Clerk-User-Email') or request.data.get("user_email")
        if not user_email:
            return Response(
                {"error": "User email is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Call the vending machine method to check and create a user record if needed
        vending_machine.ensure_user_record(user_email)

        return Response(
            {"message": f"User record ensured for {user_email}."},
            status=status.HTTP_200_OK
        )


class TransactionsView(APIView):
    """
    API view to get upto last five transactions for a given user.
    """
    def get(self, request):
        # get email from our query
        email = request.GET.get('email')
        if not email:
            return Response(
                {"success": False, "message": "Email required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        try:
            transactions, total_spent = vending_machine.get_user_transactions(email)
            return Response({"success": True, "transactions": transactions, "total_spent": float(total_spent)})
        except Exception as e:
            return Response({"success": False, "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentConfirmationView(APIView):
    """
    API view to finalize the transaction after a successful payment.
    Expects a POST request with 'user_email'.
    """
    def post(self, request):
        user_email = request.data.get("user_email")
        if not user_email:
            return Response({"success": False, "message": "User email is required."},
                            status=status.HTTP_400_BAD_REQUEST)

        result = vending_machine.finalize_transaction(user_email)
        if result.get("success"):
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)
