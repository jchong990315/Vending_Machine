# api/admin_functions.py
from sqlalchemy import text
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .db import get_engine
from .serializers import (ThresholdSerializer, InventorySerializer, PriceSerializer,
                          ChannelSerializer)
from VmachineCLI import load_inventory_and_description_from_db


class ProductView(APIView):
    """Allows admin to see all of the current available products"""

    def get(self, request):
        engine = get_engine()
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM inventory"))
                products = [dict(row) for row in result]
                return Response(products, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"error": "Failed to fetch products"},
                status=status.HTTP_400_BAD_REQUEST
            )


class InventoryUpdateView(APIView):
    """Allows admin to update inventory"""

    def post(self, request):
        tester = -1
        # set engine and serializer
        engine = get_engine()
        serializer = InventorySerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        product_name = serializer.validated_data['product_name']
        quantity = serializer.validated_data['quantity']

        try:
            tester += 1
            with engine.begin() as conn:
                # check if the specified product exists
                result = conn.execute(text("""
                    SELECT item_name FROM Inventory WHERE item_name = :product_name
                """), {"product_name": product_name})

                tester += 1

                if result is None:
                    return Response({"error": "Failed to fetch products"},
                                    status=status.HTTP_400_BAD_REQUEST)

                tester += 2
                # changes the inventory based on the spec ification

                conn.execute(text("""
                    UPDATE Inventory
                    SET stock = :quantity
                    WHERE item_name = :product_name
                """), {"quantity": quantity,
                       "product_name": product_name})

                tester += 3

                # Reload inventory after update
                if not load_inventory_and_description_from_db():
                    return Response(
                        {"error": "Failed to reload inventory after update"},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR
                    )

                return Response({f"Changed inventory of {product_name}"}, status=status.HTTP_200_OK)

        except Exception:
            return Response(
                {"error": "Failed to change inventory"},
                status=status.HTTP_400_BAD_REQUEST
            )

    def get(self, request):
        engine = get_engine()

        try:
            with engine.begin() as conn:
                result = conn.execute(text("""
                SELECT i_id, item_name, stock, price, threshold, channel
                FROM Inventory
                """))

                # Build table output
                headers = ["ID", "Item Name", "Stock", "Price", "Threshold", "Channel"]
                rows = [dict(row) for row in result.mappings()]

                # Format table
                table = []
                table.append("|".join(f"{h:^12}" for h in headers))
                table.append("-" * (12 * len(headers) + (len(headers) - 1)))
                for row in rows:
                    table.append(
                        "|".join([
                        f"{row['i_id']:^12}",
                        f"{row['item_name']:^12}",
                        f"{row['stock']:^12}",
                        f"${row['price']:^12.2f}",
                        f"{row['threshold']:^12}",
                        f"{row['channel']:^12}"
                        ])
                    )
                return Response(
                    {"inventory": "\n".join(table)},
                    status=status.HTTP_200_OK
                )

        except Exception as e:
            return f"Database error: {e}"


class PriceUpdateView(APIView):
    """Helps admin change the price for the specified product"""

    def post(self, request):
        # Tester variable that increments so that admin can bebug and know what problems there are

        tester = -1
        # setting up engine and serializer
        engine = get_engine()
        serializer = PriceSerializer(data=request.data)
        # checking if the serializer is valid

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        tester += 1
        # getting variables from serializer
        product_name = serializer.validated_data['product_name']
        price = serializer.validated_data['price']

        try:
            tester += 1
            with engine.begin() as conn:
                result = conn.execute(text("""
                    SELECT item_name FROM Inventory
                    WHERE item_name = :product_name
                """), {"product_name": product_name})

                tester += 1

                if result is None:
                    return Response({"error": "Failed to fetch products"},
                                    status=status.HTTP_400_BAD_REQUEST)

                tester += 1
                # Changing the stock of the item

                conn.execute(text("""
                    UPDATE Inventory
                    SET price = :price
                    WHERE item_name = :product_name
                """), {"price": price,
                       "product_name": product_name})

                return Response({f"Changed price of {product_name}"}, status=status.HTTP_200_OK)

        except Exception:
            return Response(
                {"error": "Failed to change inventory"},
                status=status.HTTP_400_BAD_REQUEST
            )


class ThresholdUpdateView(APIView):
    def post(self, request):
        """Helps admin set the threshold that would remind them when the stock is down a certain point"""
        tester = -1
        engine = get_engine()
        serializer = ThresholdSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        tester += 1

        product_name = serializer.validated_data['product_name']
        threshold = serializer.validated_data['threshold']

        try:
            tester += 1
            with engine.begin() as conn:
                result = conn.execute(text("""
                    SELECT item_name FROM Inventory
                    WHERE item_name = :product_name
                """), {"product_name": product_name})

                tester += 1

                if result is None:
                    return Response({"error": "Failed to fetch products"},
                                    status=status.HTTP_400_BAD_REQUEST)

                tester += 1

                conn.execute(text("""
                    UPDATE Inventory
                    SET threshold = :threshold
                    WHERE item_name = :product_name
                """), {"threshold": threshold,
                       "product_name": product_name})

                return Response({f"Changed threshold of {product_name}"}, status=status.HTTP_200_OK)

        except Exception:
            return Response(
                {"error": "Failed to change inventory"},
                status=status.HTTP_400_BAD_REQUEST
            )


class ChannelUpdateView(APIView):

    def post(self, request):
        """Helps admin set the value of channel into the product"""

        engine = get_engine()
        serializer = ChannelSerializer(data=request.data)

        # checking if the serializer is valid
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # getting values from serializer
        channel = serializer.validated_data['channel']
        product_name = serializer.validated_data['product_name']

        try:
            with engine.begin() as conn:

                # changes the channel of the inventory
                conn.execute(text("""
                    UPDATE Inventory
                    SET channel = :channel
                    WHERE item_name = :product_name
                """), {"product_name": product_name, "channel": channel})

                return Response({f"Changed threshold of items with channel {channel}"}, status=status.HTTP_200_OK)
        except Exception:
            return Response(
                {"error": "Failed to change inventory. Try another channel."},
                status=status.HTTP_400_BAD_REQUEST
            )
        

class WarningView(APIView):
    """Helps admin get warning for items below the threshold"""
    def get(self, request):
        engine = get_engine()

        with engine.begin() as conn:
            result = conn.execute(text("""
                SELECT item_name
                FROM Inventory
                WHERE stock <= threshold
                ORDER BY stock ASC
            """))

            items = [row[0] for row in result]

            return Response(
                {"low_stock_items": ", ".join(items)},
                status=status.HTTP_200_OK
            )
