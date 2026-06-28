import os
from uuid import uuid4

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, Query

from app.models import Customer, CustomerCreate, Order, OrderCreate, Product

load_dotenv()

EXPECTED_API_KEY = os.getenv("API_KEY", "dev-secret")


def verify_api_key(x_api_key: str | None = Header(default=None)) -> None:
    """Simple internal API-key check. Replace with OAuth/JWT in production."""
    if EXPECTED_API_KEY and x_api_key != EXPECTED_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid or missing X-API-Key header")


app = FastAPI(
    title="Company Demo API",
    version="1.0.0",
    description="A small FastAPI backend that will be exposed to LLMs through MCP tools.",
    dependencies=[Depends(verify_api_key)],
)

# In-memory demo data. Replace this with your database/repository layer.
customers: dict[str, Customer] = {
    "cus_001": Customer(
        id="cus_001",
        name="Samer Hasan",
        email="samer@example.com",
        phone="+971558855290",
    ),
    "cus_002": Customer(
        id="cus_002",
        name="Hadi Saleh",
        email="hadi@example.com",
        phone="+971500000001",
    ),
}

products: dict[str, Product] = {
    "prd_001": Product(id="prd_001", name="AI Strategy Workshop", price=7500),
    "prd_002": Product(id="prd_002", name="MCP Integration Package", price=12000),
    "prd_003": Product(id="prd_003", name="Legal AI Readiness Assessment", price=9500),
}

orders: dict[str, Order] = {}


@app.get("/health")
def health() -> dict:
    return {"ok": True, "service": "company-demo-api"}


@app.get("/customers", response_model=list[Customer])
def search_customers(q: str | None = Query(default=None, description="Search by name or email")):
    if not q:
        return list(customers.values())

    needle = q.lower().strip()
    return [
        customer
        for customer in customers.values()
        if needle in customer.name.lower() or needle in customer.email.lower()
    ]


@app.get("/customers/{customer_id}", response_model=Customer)
def get_customer(customer_id: str):
    customer = customers.get(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail=f"Customer '{customer_id}' not found")
    return customer


@app.post("/customers", response_model=Customer, status_code=201)
def create_customer(payload: CustomerCreate):
    customer_id = "cus_" + uuid4().hex[:8]
    customer = Customer(id=customer_id, **payload.model_dump())
    customers[customer_id] = customer
    return customer


@app.get("/products", response_model=list[Product])
def list_products():
    return list(products.values())


@app.post("/orders", response_model=Order, status_code=201)
def create_order(payload: OrderCreate):
    if payload.customer_id not in customers:
        raise HTTPException(status_code=404, detail=f"Customer '{payload.customer_id}' not found")

    total = 0.0
    for item in payload.items:
        product = products.get(item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Product '{item.product_id}' not found")
        total += product.price * item.quantity

    order_id = "ord_" + uuid4().hex[:8]
    order = Order(
        id=order_id,
        customer_id=payload.customer_id,
        items=payload.items,
        total=round(total, 2),
    )
    orders[order_id] = order
    return order


@app.get("/orders/{order_id}", response_model=Order)
def get_order(order_id: str):
    order = orders.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail=f"Order '{order_id}' not found")
    return order


@app.get("/customers/{customer_id}/orders", response_model=list[Order])
def list_customer_orders(customer_id: str):
    if customer_id not in customers:
        raise HTTPException(status_code=404, detail=f"Customer '{customer_id}' not found")
    return [order for order in orders.values() if order.customer_id == customer_id]
