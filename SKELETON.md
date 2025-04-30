# Walking Skeleton  

## Overview  
The Walking Skeleton is a minimal implementation of the Vending Machine CLI that validates the integration between the **front end (CLI)**, **back end (API & logic)**, and **database (MySQL)**. This will serve as a proof of concept before full-scale development.  

## Goals  
- Allow a user to interact with the **CLI** to request available snacks.  
- Admin is able to make changes to the database and add products
- Send the request to the **backend** using Django, which will process it.  
- Fetch snack data from the **mysql database** and return it to the **CLI** for display.  
- Ensure all components (CLI, backend, database) are successfully connected and functional.  

## Tech Stack  
- **Frontend (CLI)**: React using numerics as user input.  
- **Backend**: Python with Django to handle requests.  
- **Database**: MySQL for storing snack inventory. 