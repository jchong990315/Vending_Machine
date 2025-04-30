import React from 'react';
import FloatingPopup from './FloatingPopup';
import ProductDisplay from './ProductDisplay';

const ProductInventoryModal = ({ isOpen, onClose, products, onBack, onSelectProduct }) => {
  if (!isOpen) return null;
  
  return (
    <FloatingPopup onClose={onClose} title="Available Products" position="left">
      <ProductDisplay 
        products={products} 
        onBack={onBack}
        onSelectProduct={onSelectProduct} 
      />
    </FloatingPopup>
  );
};

export default ProductInventoryModal;