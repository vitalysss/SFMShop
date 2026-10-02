from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProductCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    price: Decimal = Field(gt=0)
    stock: int = Field(ge=0)


class OrderCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    product_id: int
    quantity: int = Field(gt=0)


class ProductUpdate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    price: Decimal = Field(gt=0)
    stock: int = Field(ge=0)


class OrderIdsRequest(BaseModel):
    order_ids: list[int] = Field(min_length=1, max_length=100)


class ProductResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    price: Decimal
    stock: int


class ExchangeRateResponse(BaseModel):
    base: str
    target: str
    rate: float
