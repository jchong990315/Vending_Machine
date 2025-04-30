import React from "react";

function ProductDisplay({ products, onBack, onSelectProduct }) {
  return (
    <div className="product-display-container">
      <div className="product-grid">
        {products.map((product) => (
          <div
            // className={`product-card ${product.available ? 'product-available' : 'product-unavailable'}`}
            // key={product.id}
            // onClick={() => product.available ? onSelectProduct(product.name) : null}
            key={product.id}
            className={`product-card ${
              product.available ? "product-available" : "product-unavailable"
            }`}
            onClick={
              product.available
                ? () => onSelectProduct(product.name)
                : undefined
            }
            aria-disabled={!product.available}
            tabIndex={product.available ? 0 : -1}
          >
            {product.image && (
              <div className="product-image">
                <img src={product.image} alt={product.name} />
              </div>
            )}
            <h3>{product.name}</h3>
            <p className="product-price">${product.price.toFixed(2)}</p>
            <p className={product.available ? "in-stock" : "out-of-stock"}>
              {product.available ? "In Stock" : "Out of Stock"}
            </p>
            <div className="product-details">
              <h4>Product Details</h4>
              <p>
                {product.description || "Nutrition and info will appear here."}
              </p>
              <p>
                <strong>Carbohydrates:</strong> {product.carbohydrates}g
              </p>
              <p>
                <strong>Allergy Info:</strong> {product.allergy_info}
              </p>
            </div>
          </div>
        ))}
      </div>
      <div className="button-back">
        <button onClick={onBack}>Back</button>
      </div>
    </div>
  );
}

export default ProductDisplay;
