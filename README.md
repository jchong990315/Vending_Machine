# Specification Document

## TeamName

TABLE17 VENDING COMPANY

### Project Abstract

The vending machine CLI will to allow users to purchase snacks straight from the command line. We will keep track of inventory, allow users to purchase inventory, and accept credit card payments using the [Stripe API](https://docs.stripe.com/). Stretch goals include integrating hardware such as Arduino boards and motors to create an authentic vending machine replica.

### Customer

The **Vending Machine CLI** is designed for a broad range of users who prefer a fast, command-line-based way to purchase snacks.

### Specification

#### Technology Stack

Here are some sample technology stacks that you can use for inspiration:

```mermaid
flowchart RL  
subgraph Front End  
    A(React: CLI using static commands)  
end  

subgraph Back End  
    B(Python: Django with \nDjango Rest Framework)  
end  

subgraph Database  
    C[(MySQL: Running through Docker)]  
end  

A <-->|"Django"| B  
B <-->|SQLAlchemy/MYSQL| C  
```

#### Database  

The database stores inventory, user transactions, and payment details. Below is the **Entity-Relationship Diagram (ERD)** for the Vending Machine CLI system.  

```mermaid
---
title: Vending Machine Database ERD
---
erDiagram
    UserProfile ||--o{ Transaction : "makes"
    Inventory ||--o{ Transaction : "purchased in"
    
    UserProfile {
        int id 
        string email
        string transactions
    }

    Inventory {
        int i_id 
        string item_name
        decimal price
        int stock
        int threshold
    }

    Transaction {
        int t_id 
        int user_id 
        datetime transaction_date 
        decimal total
        string payment_id
        string payment_status
    }
```

#### Class Diagram

```mermaid
---
title: Sample Class Diagram for Animal Program
---
classDiagram
    class Terminal {
        - user
        - products
        - selectedProducts
        - mode
        + showMenu()
        + handleSubmit(Any e)
        + handleMenuCommand(String cmd)
        + handleProductSelection(String productName)
        + handlePayment(String email)
    }
    class Admin {
        - mode
        - products
        - inputStep
        - tempData
        + showMenu()
        + handleSetInventory(String channel )
        + handleExportReport()
        + handleThresholdItem(String channel)
    }
    class admin_views {
        + get_engine()
        + ProductView(APIView)
        + InventoryUpdateView(APIView)
        + PriceUpdateView(APIView)
        + ThresholdUpdateView(APIView)
    }
    class views {
        - base_dir
        + ProductSelectionView(APIView)
        + PaymentView(APIView)
        + CurrentSelectionView(APIView)
        + TransactionsView(APIView)
        + PaymentConfirmationView(APIView)
    }

    Terminal <|-- views
    Admin <|-- admin_views
    Admin <|-- Terminal
    Terminal <|-- Admin
```

#### Flowchart

```mermaid
---
title: Vending Machine Simplified Flow
---
graph TD;
    Logs_In[/User Logs In with Clerk/] --> Press_Button[/Presses/];
    Press_Button[/User Selects Option/] --> Go_To_Backend[Go to Backend];
    Go_To_Backend --> Query_Database[Query MySQL Database];
    Query_Database --> Retrieve_Value[Retrieve Item Value];
    Retrieve_Value --> Calculate[Calculate Payment Through Clerk];
    Calculate --> Return_To_Frontend[Return Change to Frontend];
    Return_To_Frontend --> End([End]);
```

#### Behavior

The user will press a button to decide on the specific item they want. Then the frontend UI will call a function 
from the backend. Then the backend code will get information from the database (most likely MYSQL), and get information
such as the price, item name, as well as update how many items are left. 

#### Sequence Diagram

```mermaid
sequenceDiagram

participant ReactFrontend
participant DjangoBackend
participant MySQLDatabase

ReactFrontend ->> DjangoBackend: HTTP Request (e.g., GET /api/data)
activate DjangoBackend

DjangoBackend ->> MySQLDatabase: Query (e.g., SELECT * FROM data_table)
activate MySQLDatabase

MySQLDatabase -->> DjangoBackend: Result Set
deactivate MySQLDatabase

DjangoBackend -->> ReactFrontend: JSON Response
deactivate DjangoBackend
```

### Standards & Conventions

[Style Guide & Conventions](STYLE.md)

### Project Requirements

- ✅ Users can interact with the vending machine through a browser-based terminal UI (`Terminal.js`).
- ✅ System must maintain real-time inventory in a MySQL database.
- ✅ Users can securely authenticate via Clerk and perform transactions.
- ✅ Payments must be processed through the Stripe API.
- ✅ Admins should be able to manage inventory via Django Admin or CLI.
- ✅ A local CLI interface (`VmachineCLI.py`) must replicate frontend terminal behavior.
- ✅ CI/CD via GitLab: build, test, and deploy pipeline with Docker containers.
- ✅ Must run locally using Docker Compose, including MySQL and phpMyAdmin.



### Project Architecture

```mermaid
graph TD
  subgraph Frontend[React Frontend]
    
      Start[Start App] --> ModeSelect{User/Admin Mode?}
      
      ModeSelect -->|User| UserMenu
      
      subgraph UserMode[User Mode]
        UserMenu{User Options} -->|1| DisplayProducts
        UserMenu -->|2| SelectProduct
        UserMenu -->|3| Payment
        UserMenu -->|4| ExitUser
        DisplayProducts --> UserMenu
        SelectProduct --> UserMenu
        Payment -->|Success| UserMenu
        Payment -->|Fail| UserMenu
      end
      
      subgraph AdminMode[Admin Mode]
        AuthCheck -->|Success| AdminMenu
        AuthCheck -->|Fail| ExitAdmin
        AdminMenu{Admin Options} -->|1| ViewInventory
        AdminMenu -->|2| SetInventory
        AdminMenu -->|3| SetPrice
        AdminMenu -->|6| ExportReport
        AdminMenu -->|0| ExitAdmin
        ViewInventory --> AdminMenu
        SetInventory --> AdminMenu
        SetPrice --> AdminMenu
        SetProductChannel --> AdminMenu
        SetProductThreshold --> AdminMenu
        SetChannelThreshold --> AdminMenu
        ExportReport --> AdminMenu
      end
    
  end

  subgraph Backend[Django Backend]
    B1[views.py]
    B2[serializers.py]
    B3[models.py]
    B4[VmachineCLI.py]
    B5[payments.py]

  end

  subgraph Database
    D1[(MySQL Inventory Table)]
    D2[phpMyAdmin]
    B3 -->|ORM| D1
  end

  %% Connections
  
  DisplayProducts -.->|GET /products| B1
  SelectProduct -.->|POST /select| B1
  Payment -.->|POST /payment| B5
  ViewInventory -.->|GET /inventory| B1
  SetInventory -.->|POST /inventory| B1
  SetPrice -.->|POST /price| B1
  ExportReport -.->|GET /report| B1
  
  classDef menu fill:#e6f3ff,stroke:#4da6ff;
  class UserMenu,AdminMenu,ModeSelect,AuthCheck menu;
```
