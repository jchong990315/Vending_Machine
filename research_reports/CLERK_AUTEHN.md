
# Research Report

## Role-Based Access Control with Clerk

### Summary of Work

I researched how to use Clerk’s metadata system to assign and utilize custom roles (admin vs. regular user). Then I implemented role-based access control in our React frontend by restricting access to certain UI components like the Admin Panel. This involved updating our App.js to show or hide the “Admin” toggle button, modifying Terminal.js to behave differently based on user roles, and adding strict protection inside AdminPanel.js.

### Motivation

Our project have two types of users: admins who manage the system, and general users who interact with the vending machine. We are using Clerk for authentication, so we needed a way to distinguish between user types. I explored Clerk’s publicMetadata feature, which allows us to assign custom fields like role: "admin" or role: "user" to each user. This allowed us to safely render or hide components depending on role, and prevent unauthorized access to admin-only tools.

### Time Spent

~30 minutes reading Clerk documentation and exploring the dashboard
~60 minutes implementing role checks across frontend components
~30 minutes testing different accounts (with and without publicMetadata) to ensure proper restriction

### Results

First, I updated our `App.js` file to load the currently signed-in user's metadata using the `useUser()` hook from Clerk. We use this to extract the role:

```js
const role = user?.publicMetadata?.role;
const isAdmin = role === "admin";
```
Then I only show the "Switch to Admin" button to admins:

```js
{isAdmin && (
  <button onClick={handleToggleView}>
    {isAdminView ? "Switch to Terminal" : "Switch to Admin"}
  </button>
)}
```

I also conditionally render the AdminPanel only if the user is admin:

```js
{isAdminView && isAdmin ? <AdminPanel /> : <Terminal />}
```

Next, I protected the AdminPanel.js itself. Even if someone tried to navigate directly to that component, it checks the role internally and blocks access if the user is not an admin:

```js
const { user } = useUser();
const role = user?.publicMetadata?.role;
const isAdmin = role === "admin";

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
```

To assign admin roles, I manually edited the publicMetadata of test users in the Clerk dashboard:

```js
{
  "role": "admin"
}
```

By default, new users have no role assigned, so they are treated as regular users.

This system prevents unauthorized access while allowing easy role management via the Clerk dashboard.

### Sources

- Clerk[^1]
- Create a Simple Authentication System for your Nest Application with Clerk[^2]

[^1]: https://clerk.com/docs/organizations/roles-permissions
[^2]: https://dev.to/drprime01/create-a-simple-authentication-system-for-your-next-application-with-clerk-4g75