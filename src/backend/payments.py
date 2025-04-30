import stripe
import os

stripe.api_key = REMOVED_SECRET


def process_payment(product_name, amount, user_email):
    try:
        payment_intent = stripe.PaymentIntent.create(
            amount=amount,  # Convert to cents
            currency="usd",
            receipt_email=user_email,
            payment_method_types=["card"],
        )
        # helps for better handling of payment intents
        return {
            "success": True,
            "paymentIntent": {
                "id": payment_intent.id,
                "client_secret": payment_intent.client_secret,
                # Status of this PaymentIntent, one of requires_payment_method, requires_confirmation,
                # requires_action, processing, requires_capture, canceled, or succeeded.
                "status": payment_intent.status
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}
