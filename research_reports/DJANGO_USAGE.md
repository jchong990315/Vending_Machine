# How to Create Django Endpoints

## Step 1: Create Serializers
**File**: `api/serializers.py`

Example:
- Create an `ProductSerializer` to handle product data
- Add a `ProductSelectionSerializer` for product selection requests
- Add a `PaymentSerializer` for payment processing requests

## Step 2: Create API Views (Endpoints)
**File**: `api/views.py`

Example:
- `ProductListView(APIView):` view to list all products
- `ProductSelectionView(APIView):` view to handle product selection
- `PaymentView(APIView):` view to handle payments
- `CurrentSelectionView(APIView):` view to get the current selection
- Move your core business logic from the CLI class into these views

## Step 3: Define API URL Routes
**File**: `api/urls.py`

Example:
- Create URL patterns for each of your views:
  - `products/` for getting all products
  - `select-product/` for selecting a product
  - `pay/` for processing payments
  - `current-selection/` for checking the currently selected item

## Step 4: Include API URLs in Main URLs
**File**: `vending_api/urls.py`

Example:
- Make sure to include the API URLs in your main URL configuration
- Add the path prefix to all your API routes ex. `/api/`


## Frontend Integration

When connecting your React frontend:
- Use fetch or axios to make API calls
- Handle CORS issues by configuring Django if needed
- Implement proper error handling for API responses
- Maintain user session state for the selected products