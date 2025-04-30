import React from 'react';
import { Elements } from '@stripe/react-stripe-js';
import { loadStripe } from '@stripe/stripe-js';
import CheckoutForm from './CheckoutForm';

// Initialize Stripe with your publishable key
const stripePromise = REMOVED_SECRET // Replace with your actual key

const StripePaymentForm = ({ clientSecret, onComplete }) => {
  return (
    <Elements stripe={stripePromise}>
      <CheckoutForm clientSecret={clientSecret} onComplete={onComplete} />
    </Elements>
  );
};

export default StripePaymentForm;