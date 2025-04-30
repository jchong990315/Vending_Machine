import React, { useState, useEffect, useRef } from "react";
import "./Terminal.css";
import axios from "axios";
import { useUser } from "@clerk/clerk-react";

const API_BASE_URL = "http://127.0.0.1:8000/api";

function AdminPanel() {
  const terminalRef = useRef(null);
  const [input, setInput] = useState("");
  const [history, setHistory] = useState([]);
  const [mode, setMode] = useState("welcome");
  const [products, setProducts] = useState([]);
  const [inputStep, setInputStep] = useState(null);
  const [tempData, setTempData] = useState({});

  const { user } = useUser();
  const role = user?.publicMetadata?.role;
  const isAdmin = role === "admin";

  useEffect(() => {
    if (!isAdmin) return;
    addLine("Hi, I am T17 Admin Terminal – What can I do for you today?");
    fetchProducts();
    showMenu();
  }, [isAdmin]);

  useEffect(() => {
    if (!isAdmin || !terminalRef.current) return;
    terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
  }, [history, isAdmin]);

  const addLine = (line) => setHistory((prev) => [...prev, line]);

  const fetchProducts = async () => {
    try {
      const res = await axios.get(`${API_BASE_URL}/products/`);
      setProducts(res.data);
    } catch {
      addLine("Failed to load product list.");
    }
  };

  const showInventory = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/update-inventory/`);
      // The response contains a pre-formatted table string in response.data.inventory
      const tableLines = response.data.inventory.split("\n");
      addLine("→ Current Inventory:");
      tableLines.forEach((line) => addLine(line));
    } catch (error) {
      addLine("Failed to fetch inventory:");
      if (error.response) {
        addLine(`Server error: ${error.response.status}`);
        addLine(JSON.stringify(error.response.data));
      } else if (error.request) {
        addLine("No response received from server");
      } else {
        addLine(`Request setup error: ${error.message}`);
      }
    }

    showMenu();
  };

  const exportReport = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/update-inventory/`);
      const tableString = response.data.inventory;

      const response1 = await axios.get(`${API_BASE_URL}/warning/`);
      const tableString1 = response1.data.low_stock_items;

      // Display in terminal
      addLine("→ Current Inventory:");
      tableString.split("\n").forEach((line) => addLine(line));
      addLine("\n\n Low Stock Items: " + tableString1);  // Added warning line

      // Create and trigger download
      const downloadTextFile = () => {
        // Combine both strings for download
        const combinedContent = tableString + "\n\nLow Stock Items: " + tableString1;
        const blob = new Blob([combinedContent], { type: 'text/plain' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'inventory_report.txt';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
      };

      downloadTextFile();
    } catch (error) {
      addLine("Failed to fetch inventory:");
      if (error.response) {
        addLine(`Server error: ${error.response.status}`);
        addLine(JSON.stringify(error.response.data));
      } else if (error.request) {
        addLine("No response received from server");
      } else {
        addLine(`Request setup error: ${error.message}`);
      }
    }
  
    showMenu();
  };

  const showMenu = () => {
    addLine("1. View Inventory");
    addLine("2. Set Inventory");
    addLine("3. Set Price");
    addLine("4. Set Product in Channel");
    addLine("5. Set Product Threshold");
    addLine("6. Export Purchase Report");
    addLine("7. Exit");
    setMode("menu");
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const trimmed = input.trim();
    addLine(`Admin:~$ ${trimmed}`);
    setInput("");

    if (inputStep === "set-inventory-quantity") {
      const quantity = parseInt(trimmed);
      if (isNaN(quantity))
        return addLine("Invalid quantity. Please enter a number.");
      let response;

      try {
        response = await axios.post(`${API_BASE_URL}/update-inventory/`, {
          product_name: tempData,
          quantity: quantity,
        });

        addLine(response.data);
        fetchProducts();
      } catch (error) {
        if (error.response) {
          // The request was made and the server responded with a status code
          addLine(
            `Failed to update inventory - Server responded with: ${error.response.status}`
          );
          addLine(JSON.stringify(error.response.data));
        } else if (error.request) {
          // The request was made but no response was received
          addLine("Failed to update inventory - No response received");
        } else {
          // Something happened in setting up the request
          addLine(`Failed to update inventory - Error: ${error.message}`);
        }
      }
      setInputStep(null);
      setTempData({});
      showMenu();
      return;
    } else if (inputStep === "set-inventory-price") {
      const price = parseFloat(trimmed);
      if (isNaN(price)) return addLine("Invalid price. Please enter a float.");
      let response;

      try {
        response = await axios.post(`${API_BASE_URL}/update-price/`, {
          product_name: tempData,
          price: price,
        });

        addLine(response.data);
        fetchProducts();
      } catch (error) {
        if (error.response) {
          // The request was made and the server responded with a status code
          addLine(
            `Failed to update inventory - Server responded with: ${error.response.status}`
          );
          addLine(JSON.stringify(error.response.data));
        } else if (error.request) {
          // The request was made but no response was received
          addLine("Failed to update inventory - No response received");
        } else {
          // Something happened in setting up the request
          addLine(`Failed to update inventory - Error: ${error.message}`);
        }
      }
      setInputStep(null);
      setTempData({});
      showMenu();
      return;
    } else if (inputStep === "set-inventory-threshold") {
      const threshold = parseInt(trimmed);
      if (isNaN(threshold))
        return addLine("Invalid price. Please enter an integer.");
      let response;

      try {
        response = await axios.post(`${API_BASE_URL}/update-threshold/`, {
          product_name: tempData,
          threshold: threshold,
        });

        addLine(response.data);
        fetchProducts();
      } catch (error) {
        if (error.response) {
          // The request was made and the server responded with a status code
          addLine(
            `Failed to update inventory - Server responded with: ${error.response.status}`
          );
          addLine(JSON.stringify(error.response.data));
        } else if (error.request) {
          // The request was made but no response was received
          addLine("Failed to update inventory - No response received");
        } else {
          // Something happened in setting up the request
          addLine(`Failed to update inventory - Error: ${error.message}`);
        }
      }
      setInputStep(null);
      setTempData({});
      showMenu();
      return;
    } else if (inputStep === "set-channel") {
      const name = trimmed

      addLine(name)

      let response;

      try {
        response = await axios.post(`${API_BASE_URL}/update-channel/`, {
          product_name: name,
          channel: tempData,
        });

        addLine(response.data);
        fetchProducts();
      } catch (error) {
        if (error.response) {
          // The request was made and the server responded with a status code
          addLine(
            `Failed to update inventory - Server responded with: ${error.response.status}`
          );
          addLine(JSON.stringify(error.response.data));
        } else if (error.request) {
          // The request was made but no response was received
          addLine("Failed to update inventory - No response received");
        } else {
          // Something happened in setting up the request
          addLine(`Failed to update inventory - Error: ${error.message}`);
        }
      }
      setInputStep(null);
      setTempData({});
      showMenu();
      return;
    }

    switch (mode) {
      case "menu":
      case "welcome":
        handleMenu(trimmed);
        break;
      case "set-inventory":
        handleSetInventory(trimmed);
        break;
      case "set-price":
        handleSetPrice(trimmed);
        break;
      case "set-product":
        handleSetProduct(trimmed);
        break;
      case "threshold-item":
        handleThresholdItem(trimmed);
        break;
      case "threshold-channel":
        handleThresholdChannel(trimmed);
        break;
      case "report":
        handleExportReport(trimmed);
        break;
      default:
        addLine("Unknown mode. Returning to main menu.");
        showMenu();
    }
  };

  const handleMenu = (cmd) => {
    switch (cmd) {
      case "1":
        showInventory();

        break;
      case "2":
        addLine("Enter product name to update inventory:");
        setMode("set-inventory");
        break;
      case "3":
        addLine("Enter product name to update price:");
        setMode("set-price");
        break;
      case "4":
        addLine("Enter channel name to assign a product:");
        setMode("set-product");
        break;
      case "5":
        addLine("Enter product name to set threshold:");
        setMode("threshold-item");
        break;
      case "6":
        addLine("Exporting purchase report...");
        exportReport();
        break;
      case "7":
        addLine("Session ended. Goodbye.");
        setMode("exit");
        break;
      default:
        addLine("Invalid command.");
        showMenu();
    }
  };

  const handleSetInventory = (name) => {
    const product = products.find(
      (p) => p.name.toLowerCase() === name.toLowerCase()
    );
    if (!product) return addLine("Product not found.");

    setTempData(name);

    addLine(`Enter new quantity for ${name}:`);
    setInputStep("set-inventory-quantity");
  };

  const handleSetPrice = async (name) => {
    const product = products.find(
      (p) => p.name.toLowerCase() === name.toLowerCase()
    );
    if (!product) return addLine("Product not found.");

    setTempData(name);

    addLine(`Enter new price for ${name}`);
    setInputStep("set-inventory-price");
  };

  const handleSetProduct = async (channel) => {

    setTempData(channel)
    addLine("Enter product name to assign:");
    setInputStep("set-channel")
  };

  const handleThresholdItem = async (name) => {
    const product = products.find(
      (p) => p.name.toLowerCase() === name.toLowerCase()
    );
    if (!product) return addLine("Product not found.");

    setTempData(name);

    addLine(`Enter new threshold for ${name}`);
    setInputStep("set-inventory-threshold");
  };

  const handleThresholdChannel = async (channel) => {
    const thres = prompt(`Enter threshold for channel ${channel}:`);
    if (!thres || isNaN(thres)) return addLine("Invalid threshold.");
    try {
      await axios.post(`${API_BASE_URL}/channel/${channel}/threshold`, {
        threshold: parseInt(thres),
      });
      addLine(`Threshold for ${channel} set to ${thres}`);
    } catch {
      addLine("Failed to update threshold.");
    }
    showMenu();
  };

  const handleExportReport = async () => {
    exportReport()
  };

  // restrict non-admin users directly accessing through url
  if (!isAdmin) {
    return (
      <div className="terminal-frame">
        <div className="terminal-titlebar">
          <span className="title">Access Denied</span>
        </div>
        <div className="terminal-container">
          <p style={{ color: "red", padding: "1rem" }}>
            You do not have permission to access the admin panel.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="terminal-frame">
      <div className="terminal-titlebar">
        <div className="buttons">
          <span className="button close" />
          <span className="button minimize" />
          <span className="button maximize" />
        </div>
        <span className="title">Admin Terminal</span>
      </div>

      <div className="terminal-container" ref={terminalRef}>
        {history.map((line, i) => (
          <div className="terminal-line" key={i}>
            {line}
          </div>
        ))}

        {mode !== "exit" && (
          <form onSubmit={handleSubmit} className="terminal-input-line">
            <span className="prompt">Admin:~$ </span>
            <input
              className="terminal-input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              autoFocus
            />
          </form>
        )}
      </div>
    </div>
  );
}

export default AdminPanel;
