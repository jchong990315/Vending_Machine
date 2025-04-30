import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import AdminPanel from "./AdminPanel";
import { useUser } from "@clerk/clerk-react";
import axios from "axios";

// Mock the Clerk useUser hook and axios module
jest.mock("@clerk/clerk-react", () => ({
  useUser: jest.fn(),
}));

jest.mock("axios");

describe("AdminPanel Component", () => {
  beforeEach(() => {
    // Clear all mocks before each test to avoid interference
    jest.clearAllMocks();
  });

  test("shows access denied if user is not admin", () => {
    // Simulate a non-admin user
    useUser.mockReturnValue({
      user: { publicMetadata: { role: "user" } },
    });

    render(<AdminPanel />);

    // Expect the 'Access Denied' message to be rendered
    expect(screen.getByText(/you do not have permission/i)).toBeInTheDocument();
  });

  test("renders terminal and shows welcome + menu if user is admin", async () => {
    // Simulate an admin user
    useUser.mockReturnValue({
      user: { publicMetadata: { role: "admin" } },
    });

    // Mock the products API to return an empty list
    axios.get.mockResolvedValue({ data: [] });

    render(<AdminPanel />);

    // Wait for the welcome message and menu options to appear
    await waitFor(() => {
      expect(screen.getByText(/what can i do for you/i)).toBeInTheDocument();
      expect(screen.getByText(/1. View Inventory/i)).toBeInTheDocument();
    });
  });

  test("handles inventory view command", async () => {
    // Simulate an admin user
    useUser.mockReturnValue({
      user: { publicMetadata: { role: "admin" } },
    });

    // Mock product data with actual values
    axios.get.mockResolvedValue({
      data: [
        { id: 1, name: "Coke", quantity: 20, price: 1.5 },
        { id: 2, name: "Chips", quantity: 10, price: 1.0 },
      ],
    });

    render(<AdminPanel />);

    // Wait for the menu to be loaded
    await waitFor(() => {
      expect(screen.getByText(/view inventory/i)).toBeInTheDocument();
    });

    // Simulate typing "1" and submitting it to trigger inventory view
    const input = screen.getByRole("textbox");
    fireEvent.change(input, { target: { value: "1" } });
    fireEvent.submit(input);

    // Expect the product inventory info to be displayed
    await waitFor(() => {
      expect(screen.getByText(/Coke.*\$1.50.*Qty: 20/i)).toBeInTheDocument();
      expect(screen.getByText(/Chips.*\$1.00.*Qty: 10/i)).toBeInTheDocument();
    });
  });
});
