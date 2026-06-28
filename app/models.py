from pydantic import BaseModel, EmailStr, Field
from typing import Literal


class CustomerCreate(BaseModel):
    name: str = Field(..., min_length=2, examples=["Samer Hasan"])
    email: EmailStr = Field(..., examples=["samer@example.com"])
    phone: str | None = Field(default=None, examples=["+971558855290"])


class Customer(CustomerCreate):
    id: str
    status: Literal["active", "inactive"] = "active"


class Product(BaseModel):
    id: str
    name: str
    price: float
    currency: str = "AED"


class OrderLine(BaseModel):
    product_id: str
    quantity: int = Field(..., ge=1, le=100)


class OrderCreate(BaseModel):
    customer_id: str
    items: list[OrderLine]


class Order(BaseModel):
    id: str
    customer_id: str
    items: list[OrderLine]
    total: float
    currency: str = "AED"
    status: Literal["created", "paid", "cancelled"] = "created"
