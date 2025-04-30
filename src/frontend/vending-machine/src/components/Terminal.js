import React, { useState, useEffect, useRef } from "react";
import "./Terminal.css";
import axios from "axios";
import { useUser } from "@clerk/clerk-react";
import ProductDisplay from "./ProductDisplay";
import ProductInventoryModal from "./ProductInventoryModal";
import PaymentModal from "./PaymentModal";

// API base URL
const API_BASE_URL = "http://127.0.0.1:8000/api";

function Terminal() {
  const terminalRef = useRef(null);
  const { user } = useUser();

  // State for products (will be fetched from API)
  const [products, setProducts] = useState([]);

  // Tracks the currently selected product
  const [selectedProduct, setSelectedProduct] = useState(null);

  // Track the option
  const [mode, setMode] = useState("welcome");

  // Terminal history
  const [history, setHistory] = useState([]);

  // User input
  const [input, setInput] = useState("");

  // Controls whether the floating popup is open
  const [isPopupOpen, setIsPopupOpen] = useState(false);

  //total spent
  const [totalSpent, setTotalSpent] = useState(0);

  // Payment modal state
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [paymentClientSecret, setPaymentClientSecret] = useState("");

  // Scroll to the bottom of the terminal
  const scrollToBottom = () => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  };

  //for transactions
  const [transactions, setTransactions] = useState([]);

  const KICK_RESPONSES = [
    "Ouch! That hurts!",
    "Hey! Careful with that!",
    "*Clang* — you really kicked me, huh?",
    "I’m just a machine — that was a little violent!",
  ];

  function getKickResponse() {
    const idx = Math.floor(Math.random() * KICK_RESPONSES.length);
    return KICK_RESPONSES[idx];
  }

  // Function to fetch transactions
  const fetchTransactions = () => {
    if (user) {
      axios
        .get(
          `${API_BASE_URL}/transactions?email=${user.primaryEmailAddress.emailAddress}`
        )
        .then((response) => {
          setTransactions(response.data.transactions);
          setTotalSpent(
            response.data.total_spent !== undefined
              ? response.data.total_spent
              : 0
          );
        })
        .catch((error) => console.error("Error fetching transactions:", error));
    }
  };

  // New function to handle product selection from the popup
  const handleProductSelectFromPopup = (productName) => {
    // Close the popup
    setIsPopupOpen(false);
    // Use the existing API call function
    handleProductSelection(productName);
  };

  useEffect(() => {
    if (user) {
      fetchTransactions();
    }
  }, [user]);

  // Call scrollToBottom whenever history changes
  useEffect(() => {
    scrollToBottom();
  }, [history]);

  useEffect(() => {
    // Add welcome message
    addLineToHistory(
      "Hi I am T17 Vending Machine - What can I dispense for you today?"
    );

    // Fetch products from API
    fetchProducts();

    // Show menu
    showMenu();
  }, []);

  useEffect(() => {
    if (user) {
      // Send a POST request to ensure the user record exists
      axios
        .post(
          `${API_BASE_URL}/user-profile/`,
          {},
          {
            headers: {
              "X-Clerk-User-Email": user.primaryEmailAddress.emailAddress,
            },
          }
        )
        .then((response) => {
          console.log("User profile ensured:", response.data.message);
        })
        .catch((error) => {
          console.error("Error ensuring user profile:", error);
        });
    }
  }, [user]);

  // Function to fetch products from API
  const fetchProducts = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/products/`);
      console.log("Fetched products:", response.data);
      const withAvailability = response.data.map((product) => ({
        ...product,
        available: product.stock > 0,
      }));
      setProducts(withAvailability);
    } catch (error) {
      console.error("Error fetching products:", error);
      addLineToHistory("Error: Could not fetch products from server.");
    }
  };

  // Append a new line to the history
  function addLineToHistory(line) {
    setHistory((prev) => [...prev, line]);
  }

  // Show the main menu
  function showMenu() {
    addLineToHistory("1. Display all products");
    addLineToHistory("2. Select a product");
    addLineToHistory("3. Pay for product(s)");
    addLineToHistory("4. Kick the machine");
    addLineToHistory("5. Exit");
    setMode("menu");
  }

  // Handle form submission
  function handleSubmit(e) {
    e.preventDefault();
    const trimmed = input.trim();

    // Show the user's input in the terminal
    addLineToHistory("> " + trimmed);

    switch (mode) {
      case "welcome":
      case "menu":
        handleMenuCommand(trimmed);
        break;
      case "selectingProduct":
        handleProductSelection(trimmed);
        break;
      case "paying":
        handlePayment(trimmed);
        break;
      default:
        addLineToHistory("Command not found, try again.");
        showMenu();
        break;
    }

    // Reset the input field
    setInput("");
  }

  // Handle menu commands
  function handleMenuCommand(cmd) {
    const choice = parseInt(cmd, 10);
    if (isNaN(choice)) {
      addLineToHistory("Command not found, try again.");
      showMenu();
      return;
    }

    switch (choice) {
      case 1:
        // Open the floating popup instead of navigating away
        setIsPopupOpen(true);
        break;

      case 2:
        // Select a product
        addLineToHistory(
          "Please enter the name of the product you want to select:"
        );
        setMode("selectingProduct");
        break;

      case 3:
        // Process payment
        if (!selectedProduct) {
          addLineToHistory(
            "No product selected. Please select a product first."
          );
          showMenu();
        } else {
          addLineToHistory("Please enter your email for the receipt:");
          setMode("paying");
        }
        break;

      case 5:
        // Exit
        addLineToHistory("Thank you, come again!");
        setMode("exiting");
        break;

      case 4:
        addLineToHistory(getKickResponse());
        showMenu();
        break;

      default:
        addLineToHistory("Command not found, try again.");
        showMenu();
        break;
    }
  }

  // Handle product selection
  async function handleProductSelection(productName) {
    try {
      const isChannel = /^[A-Ma-m][1-8]$/.test(productName.trim());
      const response = await axios.post(`${API_BASE_URL}/select-product/`, {
        [isChannel ? "channel" : "product_name"]: productName.toLowerCase(),
      });

      addLineToHistory(response.data.message);
      setSelectedProduct(productName.toLowerCase());
    } catch (error) {
      if (error.response && error.response.data) {
        addLineToHistory(
          `Error: ${error.response.data.message || "Product not found"}`
        );
      } else {
        addLineToHistory("Error: Could not select product.");
      }
    }

    showMenu();
  }

  // Handle payment completion
  async function handlePaymentComplete(result) {
    setShowPaymentModal(false);

    if (result.error) {
      addLineToHistory(`Payment failed: ${result.error.message}`);
    } else if (
      result.paymentIntent &&
      result.paymentIntent.status === "succeeded"
    ) {
      try {
        const confirmationResponse = await axios.post(
          `${API_BASE_URL}/confirm-payment/`,
          {
            user_email: user.primaryEmailAddress.emailAddress,
          }
        );
        if (confirmationResponse.data.success) {
          addLineToHistory(confirmationResponse.data.message);
          setSelectedProduct(null);
          // we need to update the state after we handle a complete payment.
          fetchTransactions();
        } else {
          addLineToHistory(`Error: ${confirmationResponse.data.message}`);
        }
      } catch (error) {
        addLineToHistory("Error finalizing transaction.");
        console.error("Finalization error:", error);
      }
    } else {
      addLineToHistory("Payment is being processed.");
    }
    await fetchProducts();
    showMenu();
  }

  // Handle payment
  async function handlePayment(email) {
    try {
      // Validate email format (simple check)
      if (!email.includes("@")) {
        addLineToHistory("Error: Please enter a valid email address.");
        showMenu();
        return;
      }

      const response = await axios.post(`${API_BASE_URL}/pay/`, {
        user_email: email,
      });

      if (response.data.success && response.data.client_secret) {
        // Store the client secret and show payment modal
        setPaymentClientSecret(response.data.client_secret);
        setShowPaymentModal(true);
        addLineToHistory(
          "Payment processing. Please complete the payment in the modal."
        );
      } else {
        addLineToHistory(response.data.message);

        // Reset selected product if payment was successful
        if (response.data.success) {
          setSelectedProduct(null);
          showMenu();
        }
      }
    } catch (error) {
      if (error.response && error.response.data) {
        addLineToHistory(
          `Error: ${error.response.data.message || "Payment failed"}`
        );
      } else {
        addLineToHistory("Error: Could not process payment.");
      }
      showMenu();
    }
  }

  return (
    <div className="terminal-frame">
      <div className="terminal-titlebar">
        <div className="buttons">
          <span className="button close"></span>
          <span className="button minimize"></span>
          <span className="button maximize"></span>
        </div>
        <span className="title">Terminal</span>
        <div className="dropdown-container">
          <button className="dropdown-button">Account</button>
          <div className="dropdown-content">
            <div className="dropdown-header">
              Hi {user ? user.primaryEmailAddress.emailAddress : "Guest"}!
            </div>
            {transactions.length > 0 ? (
              <>
                <div className="transactions-header">
                  Here are your past transactions:
                </div>
                <ul className="transaction-list">
                  {transactions.map((transaction, idx) => (
                    <li key={idx}>
                      {transaction.item} - ${transaction.cost}
                    </li>
                  ))}
                </ul>
                <div className="total-spent">
                  Total Spent: ${totalSpent.toFixed(2)}
                </div>
              </>
            ) : (
              <div className="no-transactions">No recent transactions.</div>
            )}
          </div>
        </div>
      </div>
      <div className="terminal-container" ref={terminalRef}>
        {history.map((line, idx) => (
          <div key={idx} className="terminal-line">
            {line}
          </div>
        ))}
        {mode !== "exiting" && (
          <form onSubmit={handleSubmit} className="terminal-input-line">
            <span className="prompt">Vending:~$ </span>
            <input
              type="text"
              className="terminal-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              autoFocus
            />
          </form>
        )}
      </div>

      {/* Product Inventory Modal */}
      <ProductInventoryModal
        isOpen={isPopupOpen}
        onClose={() => setIsPopupOpen(false)}
        products={products}
        onBack={() => setIsPopupOpen(false)}
        onSelectProduct={handleProductSelectFromPopup}
      />

      {/* Payment Modal */}
      <PaymentModal
        isOpen={showPaymentModal}
        onClose={() => setShowPaymentModal(false)}
        clientSecret={paymentClientSecret}
        onComplete={handlePaymentComplete}
      />
    </div>
  );
}

export default Terminal;
