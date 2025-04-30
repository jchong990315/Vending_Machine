# Stripe API Research
For the full usage docs refer here: https://docs.stripe.com/api?lang=python

### Basics
The modern Stripe API utilizes the PaymentIntent object to show the customer's
intent to pay. This is how the process works to accept payment: 
1. You first need to show what method you are going to pay with
2. You then confirm that the customer is going to pay (usually with the pay button)
3. Your intent will now be in the processing state
- If the payment fails you can retry without creating new PaymentIntent objects
- If the payment succeeds the payment worked as planned
4. We finally use the Event object to show whether the payment failed or succeeded

### Usage
1. Create a stripe account and create an API key (stripe uses API keys to authenticate requests)  
- Use your API key by assigning it to stripe.api_key. The Python library will then automatically send this key in each request.
```python
import stripe
stripe.api_key = REMOVED_SECRET
```
2. How to install:
```bash
pip install stripe
```  
3. Creating payment intent
- When a user selects an item we need to create some sort of payment intent:
```python
def create_payment_intent(amount_in_cents):
    intent = stripe.PaymentIntent.create(
        amount=amount_in_cents,
        currency='usd',
    )
    return intent
```
4. Handling Confirmation
- After a payment intent is created the user should be asked to confirm it. We can handle a payment confirmation like this:
```python
def confirm_payment(payment_intent_id):
    intent = stripe.PaymentIntent.confirm(
        payment_intent_id,
        payment_method="pm_card_visa"  # For simplicity, assume a pre-defined payment method
    )
    return intent
```
5. Using Webhooks
- In order to receive updates about payment status from stripe we need to have a server listening to stripe.
- You can learn more about webhooks here:  https://docs.stripe.com/api/webhook_endpoints?lang=python
- In order to handle a webhook we will need to use flask/django

### Good Practice
Stripe's libraries raise a lot of exceptions for a lot of different reasons. It is important to write code that gracefully handles all possible exceptions. 
```python
try:
  # Use Stripe's library to make requests...
  pass
except stripe.error.CardError as e:
  # Since it's a decline, stripe.error.CardError will be caught

  print('Status is: %s' % e.http_status)
  print('Code is: %s' % e.code)
  # param is '' in this case
  print('Param is: %s' % e.param)
  print('Message is: %s' % e.user_message)
except stripe.error.RateLimitError as e:
  # Too many requests made to the API too quickly
  pass
except stripe.error.InvalidRequestError as e:
  # Invalid parameters were supplied to Stripe's API
  pass
except stripe.error.AuthenticationError as e:
  # Authentication with Stripe's API failed
  # (maybe you changed API keys recently)
  pass
except stripe.error.APIConnectionError as e:
  # Network communication with Stripe failed
  pass
except stripe.error.StripeError as e:
  # Display a very generic error to the user, and maybe send
  # yourself an email
  pass
except Exception as e:
  # Something else happened, completely unrelated to Stripe
  pass
```

### SDKs
There are SDKs for Node.js, Python, Java, and Android and iOS

### Client (Checkout is js)
You can initialize stripe with an API key and using fetch to request the 
server for a checkout session

```
const stripe = Stripe('pk_test_TYooMQauvdEDq54NiTphI7jx');

someMethod()

# Fetch the checkout session
async Function someMethod() {
    const fetchClientSecret = async () => {
      const response = await fetch("/create-checkout-session", {
        method: "POST",
      });
      const { clientSecret } = await response.json();
      return clientSecret;
    };
}
```

Then you can mount checkout 

### Checking PaymentIntent Status
You can check if the payment was completed by checking the PaymentIntent object
```
(async () => {
  const {paymentIntent, error} = await stripe.confirmCardPayment(clientSecret);
  if (error) {
    // Handle error here
  } else if (paymentIntent && paymentIntent.status === 'succeeded') {
    // Handle successful payment here
  }
})();
```
This function would either: 
1. Resolve with a PaymentIntent since the payment succeeded
2. Cause an error since the payment was rejected
