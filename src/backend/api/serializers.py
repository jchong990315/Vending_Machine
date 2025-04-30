# api/serializers.py
from rest_framework import serializers


# checking output
class ProductSerializer(serializers.Serializer):
    """Serializer for vending machine products"""
    name = serializers.CharField(max_length=100)
    price = serializers.FloatField()
    stock = serializers.IntegerField()
    available = serializers.BooleanField()
    description = serializers.CharField(max_length=255)
    calories = serializers.IntegerField(required=False, allow_null=True) # Allow None (null) for calories
    carbohydrates = serializers.FloatField(required=False, allow_null=True) # Allow None (null) for carbs
    allergy_info = serializers.CharField(max_length=255)
    channel = serializers.CharField(max_length=3)
    

# checking input
class ProductSelectionSerializer(serializers.Serializer):
    """Serializer for product selection input"""
    product_name = serializers.CharField(max_length=100)


# checking input
class PaymentSerializer(serializers.Serializer):
    """Serializer for payment input"""
    user_email = serializers.EmailField()


# checking input
class InventorySerializer(serializers.Serializer):
    """Serializer for admin stock change"""
    product_name = serializers.CharField(max_length=100)
    quantity = serializers.IntegerField()


# checking input
class PriceSerializer(serializers.Serializer):
    """Serializer for admin price change"""
    product_name = serializers.CharField(max_length=100)
    price = serializers.FloatField()


# checking input
class ThresholdSerializer(serializers.Serializer):
    """Serializer for admin threshold change"""
    product_name = serializers.CharField(max_length=100)
    threshold = serializers.IntegerField()


class ChannelSerializer(serializers.Serializer):
    """Serializer for admin set channel"""
    product_name = serializers.CharField(max_length=100)
    channel = serializers.CharField(max_length=100)
