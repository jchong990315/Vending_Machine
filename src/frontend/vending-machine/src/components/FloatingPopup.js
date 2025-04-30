import React from "react";
import "./FloatingPopup.css";

function FloatingPopup({ children, onClose, title = "", position = "" }) {
  // Determine the positioning class
  const positionClass = position ? `position-${position}` : "";
  
  return (
    <>
      <div className="modal-overlay" onClick={onClose}></div>
      <div className={`floating-popup ${positionClass}`}>
        <div className="floating-popup-header">
          {title && <h3 className="popup-title">{title}</h3>}
          <button className="popup-close" onClick={onClose}>×</button>
        </div>
        <div className="floating-popup-content">
          {children}
        </div>
      </div>
    </>
  );
}

export default FloatingPopup;