import React, { useState } from "react";
import Terminal from "./components/Terminal";
import AdminPanel from "./components/AdminPanel";
import "./App.css";
import {
  SignedIn,
  SignedOut,
  SignIn,
  SignOutButton,
  useUser,
} from "@clerk/clerk-react";

function App() {
  const [isAdminView, setIsAdminView] = useState(false);
  const { user } = useUser();

  const role = user?.publicMetadata?.role;
  const isAdmin = role === "admin";

  const handleToggleView = () => {
    setIsAdminView((prev) => !prev);
  };

  return (
    <div className="App">
      <SignedOut>
        <SignIn />
      </SignedOut>

      <SignedIn>
        {isAdminView && isAdmin ? <AdminPanel /> : <Terminal />}

        <div className="button-row">
          <SignOutButton>
            <button className="custom-signout">sign out</button>
          </SignOutButton>
          {isAdmin && (
            <button className="custom-signout" onClick={handleToggleView}>
              {isAdminView ? "Switch to Terminal" : "Switch to Admin"}
            </button>
          )}
        </div>
      </SignedIn>
    </div>
  );
}

export default App;
