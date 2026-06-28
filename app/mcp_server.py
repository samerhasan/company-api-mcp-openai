import os
from typing import Any

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:9000")
API_KEY = os.getenv("API_KEY", "dev-secret")

mcp = FastMCP("company-api-mcp")


async def call_api(
    method: str,
    path: str,
    *,
    json: dict[str, Any] | None = None,
    params: dict[str, Any] | None = None,
) -> dict[str, Any] | list[Any]:
    """Call the internal FastAPI service and return JSON-safe output for MCP."""
    headers = {"X-API-Key": API_KEY} if API_KEY else {}
    async with httpx.AsyncClient(base_url=API_BASE_URL, timeout=15.0) as client:
        try:
            response = await client.request(method, path, json=json, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            try:
                detail: Any = exc.response.json()
            except Exception:
                detail = exc.response.text
            return {
                "error": True,
                "status_code": exc.response.status_code,
                "detail": detail,
            }
        except httpx.RequestError as exc:
            return {
                "error": True,
                "detail": f"Could not reach API at {API_BASE_URL}: {exc}",
            }


@mcp.tool()
async def api_health() -> dict[str, Any] | list[Any]:
    """Check whether the company backend API is alive."""
    return await call_api("GET", "/health")


@mcp.tool()
async def search_customers(q: str | None = None) -> dict[str, Any] | list[Any]:
    """Search customers by name or email. Pass an empty value to list all customers."""
    params = {"q": q} if q else None
    return await call_api("GET", "/customers", params=params)


@mcp.tool()
async def get_customer(customer_id: str) -> dict[str, Any] | list[Any]:
    """Get one customer by customer ID, for example cus_001."""
    return await call_api("GET", f"/customers/{customer_id}")


@mcp.tool()
async def create_customer(name: str, email: str, phone: str | None = None) -> dict[str, Any] | list[Any]:
    """Create a new customer in the company API."""
    return await call_api(
        "POST",
        "/customers",
        json={"name": name, "email": email, "phone": phone},
    )


@mcp.tool()
async def list_products() -> dict[str, Any] | list[Any]:
    """List products/services that can be ordered."""
    return await call_api("GET", "/products")


@mcp.tool()
async def create_order(customer_id: str, product_id: str, quantity: int = 1) -> dict[str, Any] | list[Any]:
    """Create an order for a customer using a product ID and quantity."""
    return await call_api(
        "POST",
        "/orders",
        json={
            "customer_id": customer_id,
            "items": [{"product_id": product_id, "quantity": quantity}],
        },
    )


@mcp.tool()
async def get_order(order_id: str) -> dict[str, Any] | list[Any]:
    """Get one order by order ID."""
    return await call_api("GET", f"/orders/{order_id}")


@mcp.tool()
async def list_customer_orders(customer_id: str) -> dict[str, Any] | list[Any]:
    """List all orders for one customer."""
    return await call_api("GET", f"/customers/{customer_id}/orders")


if __name__ == "__main__":
    # Starts Streamable HTTP MCP endpoint at: http://127.0.0.1:8000/mcp
    mcp.run(transport="streamable-http")
