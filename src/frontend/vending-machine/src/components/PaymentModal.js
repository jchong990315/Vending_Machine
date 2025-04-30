import React from 'react';
import FloatingPopup from './FloatingPopup';
import StripePaymentForm from './StripePaymentForm';

const PaymentModal = ({ isOpen, onClose, clientSecret, onComplete }) => {
  if (!isOpen) return null;
  
  return (
    <FloatingPopup onClose={onClose} title="Complete Your Payment" position="right">
      <div className="payment-container">
        <StripePaymentForm
          clientSecret={clientSecret}
          onComplete={onComplete}
        />
      </div>
    </FloatingPopup>
  );
};

export default PaymentModal;