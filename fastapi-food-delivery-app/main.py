from fastapi import FastAPI, Query, Response
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

menu = [
    {"id": 1, "name": "Pizza", "price": 200, "category": "Pizza", "is_available": True},
    {"id": 2, "name": "Burger", "price": 120, "category": "Burger", "is_available": True},
    {"id": 3, "name": "Coke", "price": 50, "category": "Drink", "is_available": True},
    {"id": 4, "name": "Fries", "price": 90, "category": "Snack", "is_available": True},
    {"id": 5, "name": "Ice Cream", "price": 80, "category": "Dessert", "is_available": False},
    {"id": 6, "name": "Pasta", "price": 150, "category": "Italian", "is_available": True},
]

orders = []
order_counter = 1

cart = []

def find_menu_item(item_id):
    for i in menu:
        if i["id"] == item_id:
            return i
    return None

def calculate_bill(price, quantity, order_type="delivery"):
    total = price * quantity
    if order_type == "delivery":
        total += 30
    return total

def filter_menu_logic(category, max_price, is_available):
    result = menu
    if category is not None:
        result = [i for i in result if i["category"].lower() == category.lower()]
    if max_price is not None:
        result = [i for i in result if i["price"] <= max_price]
    if is_available is not None:
        result = [i for i in result if i["is_available"] == is_available]
    return result

  
class OrderRequest(BaseModel):
    customer_name: str = Field(min_length=2)
    item_id: int = Field(gt=0)
    quantity: int = Field(gt=0, le=20)
    delivery_address: str = Field(min_length=5)
    order_type: str = "delivery"

class NewMenuItem(BaseModel):
    name: str = Field(min_length=2)
    price: int = Field(gt=0)
    category: str = Field(min_length=2)
    is_available: bool = True

class CheckoutRequest(BaseModel):
    customer_name: str
    delivery_address: str

  
@app.get("/")
def home():
    return {"message": "Welcome to Food Delivery App"}


@app.get("/menu")
def get_menu():
    return {"items": menu, "total": len(menu)}

@app.get("/menu/summary")
def summary():
    available = len([i for i in menu if i["is_available"]])
    return {
        "total": len(menu),
        "available": available,
        "unavailable": len(menu) - available
    }

@app.get("/menu/filter")
def filter_menu(category: Optional[str] = None,
                max_price: Optional[int] = None,
                is_available: Optional[bool] = None):
    result = filter_menu_logic(category, max_price, is_available)
    return {"items": result, "count": len(result)}

@app.get("/menu/search")
def search(keyword: str):
    res = [i for i in menu if keyword.lower() in i["name"].lower()]
    return {"results": res, "count": len(res)}

@app.get("/menu/sort")
def sort_menu(order: str = "asc"):
    return sorted(menu, key=lambda x: x["price"], reverse=(order=="desc"))

@app.get("/menu/page")
def paginate(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    return menu[start:start + limit]

@app.get("/menu/browse")
def browse(keyword: Optional[str] = None,
           page: int = 1,
           limit: int = 3):

    data = menu

    if keyword:
        data = [i for i in data if keyword.lower() in i["name"].lower()]

    start = (page - 1) * limit
    return data[start:start + limit]

@app.get("/menu/{item_id}")
def get_item(item_id: int):
    item = find_menu_item(item_id)
    if not item:
        return {"error": "Item not found"}
    return item

  
@app.get("/orders")
def get_orders():
    return {"orders": orders, "total": len(orders)}

@app.get("/orders/search")
def search_orders(name: str):
    result = [o for o in orders if name.lower() in o["customer"].lower()]
    return {"results": result}

@app.get("/orders/sort")
def sort_orders(order: str = "asc"):
    return sorted(orders, key=lambda x: x["total_price"], reverse=(order=="desc"))

@app.post("/orders")
def create_order(order: OrderRequest):
    global order_counter

    item = find_menu_item(order.item_id)
    if not item:
        return {"error": "Item not found"}

    if not item["is_available"]:
        return {"error": "Item unavailable"}

    total = calculate_bill(item["price"], order.quantity, order.order_type)

    new_order = {
        "order_id": order_counter,
        "customer": order.customer_name,
        "item": item["name"],
        "total_price": total
    }

    orders.append(new_order)
    order_counter += 1

    return new_order

@app.post("/menu")
def add_item(item: NewMenuItem, response: Response):
    for i in menu:
        if i["name"].lower() == item.name.lower():
            return {"error": "Duplicate item"}

    new = item.dict()
    new["id"] = len(menu) + 1
    menu.append(new)
    response.status_code = 201
    return new

@app.put("/menu/{item_id}")
def update_item(item_id: int,
                price: Optional[int] = None,
                is_available: Optional[bool] = None):
    item = find_menu_item(item_id)
    if not item:
        return {"error": "Not found"}

    if price is not None:
        item["price"] = price
    if is_available is not None:
        item["is_available"] = is_available

    return item

@app.delete("/menu/{item_id}")
def delete_item(item_id: int):
    item = find_menu_item(item_id)
    if not item:
        return {"error": "Not found"}

    menu.remove(item)
    return {"message": "Deleted"}

@app.post("/cart/add")
def add_to_cart(item_id: int, quantity: int = 1):
    item = find_menu_item(item_id)
    if not item or not item["is_available"]:
        return {"error": "Invalid item"}

    for c in cart:
        if c["item_id"] == item_id:
            c["quantity"] += quantity
            return {"message": "Updated"}

    cart.append({"item_id": item_id, "quantity": quantity})
    return {"message": "Added"}

@app.get("/cart")
def view_cart():
    total = 0
    items = []
    for c in cart:
        item = find_menu_item(c["item_id"])
        cost = item["price"] * c["quantity"]
        total += cost
        items.append({"name": item["name"], "qty": c["quantity"]})
    return {"cart": items, "total": total}

@app.delete("/cart/{item_id}")
def remove_cart(item_id: int):
    for c in cart:
        if c["item_id"] == item_id:
            cart.remove(c)
            return {"message": "Removed"}
    return {"error": "Not found"}

@app.post("/cart/checkout")
def checkout(data: CheckoutRequest, response: Response):
    global order_counter

    if not cart:
        return {"error": "Cart empty"}

    result = []
    total = 0

    for c in cart:
        item = find_menu_item(c["item_id"])
        cost = item["price"] * c["quantity"]
        total += cost

        order = {
            "order_id": order_counter,
            "customer": data.customer_name,
            "item": item["name"],
            "total_price": cost
        }

        orders.append(order)
        result.append(order)
        order_counter += 1

    cart.clear()
    response.status_code = 201
    return {"orders": result, "total": total}
