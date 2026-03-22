# Food Delivery App Backend API (FastAPI)

This project is a backend API built using FastAPI for a Food Delivery System.

## Features

- View menu items
- Add, update, delete menu items (CRUD)
- Place orders with validation
- Cart system (add, view, remove, checkout)
- Order total calculation with delivery charges
- Search, filter, sort, and pagination
- Swagger UI for testing APIs

---

## Technologies Used

- Python
- FastAPI
- Pydantic
- Uvicorn

---

## API Endpoints

### Menu
- GET /menu
- GET /menu/{item_id}
- GET /menu/summary
- GET /menu/filter
- GET /menu/search
- GET /menu/sort
- GET /menu/page
- GET /menu/browse
- POST /menu
- PUT /menu/{item_id}
- DELETE /menu/{item_id}

### Orders
- GET /orders
- POST /orders
- GET /orders/search
- GET /orders/sort

### Cart
- POST /cart/add
- GET /cart
- DELETE /cart/{item_id}
- POST /cart/checkout

---

## How to Run

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
uvicorn main:app --reload

3. Open swagger UI:
http://127.0.0.1:8000/docs
