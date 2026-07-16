from decimal import Decimal

from fastapi import FastAPI
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pydantic import BaseModel
from pydantic import Field

from src.database.queries_orm import create_order
from src.database.queries_orm import delete_product
from src.database.queries_orm import update_product
from src.services.cache_service import get_cached_product
from src.services.cache_service import get_cached_products
from src.services.cache_service import invalidate_product_cache
from src.services.log_service import save_log

app = FastAPI()

def invalidate_cache_safely(product_id: int) -> None:
    try:
        invalidate_product_cache(product_id)
    except Exception as e:
        print("Не удалось очистить Redis-кэш:", e)

class OrderCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int = Field(
        gt=0,
    )


class ProductUpdate(BaseModel):
    name: str
    price: Decimal = Field(
        gt=0,
    )
    stock: int = Field(
        ge=0,
    )


@app.get("/products")
def get_products(
    limit: int = 10,
    offset: int = 0,
):
    products = get_cached_products()

    return {
        "total": len(products),
        "limit": limit,
        "offset": offset,
        "products": products[offset : offset + limit],
    }


@app.get("/products/{product_id}")
def get_product_endpoint(
    product_id: int,
):
    product = get_cached_product(product_id)

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Товар не найден",
        )

    return product


@app.post(
    "/orders",
    status_code=201,
)
def create_new_order(
    order_data: OrderCreate,
):
    order = create_order(
        user_id=order_data.user_id,
        product_id=order_data.product_id,
        quantity=order_data.quantity,
    )

    if order is None:
        write_log_safely(
            {
                "event_type": "order_failed",
                "message": "Не удалось создать заказ",
                "status_code": 400,
                "user_id": order_data.user_id,
                "product_id": order_data.product_id,
                "quantity": order_data.quantity,
            }
        )
        raise HTTPException(
            status_code=400,
            detail=(
                "Не удалось создать заказ. "
                "Проверьте пользователя, товар, "
                "остаток и баланс."
            ),
        )

    invalidate_cache_safely(order_data.product_id)

    write_log_safely(
        {
            "event_type": "order_created",
            "message": f"Заказ создан {order.id}",
            "status_code": 201,
            "user_id": order.user_id,
            "product_id": order_data.product_id,
            "quantity": order_data.quantity,
        }
    )

    return {
        "id": order.id,
        "user_id": order.user_id,
        "total": str(order.total),
        "status": order.status,
        "quantity": order_data.quantity,
        "product_id": order_data.product_id,
    }


@app.put("/products/{product_id}")
def update_product_endpoint(
    product_id: int,
    product_data: ProductUpdate,
):
    product = update_product(
        product_id=product_id,
        name=product_data.name,
        price=product_data.price,
        stock=product_data.stock,
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Товар не найден",
        )

    invalidate_cache_safely(product_id)

    return {
        "id": product.id,
        "name": product.name,
        "price": str(product.price),
        "stock": product.stock,
    }


@app.delete("/products/{product_id}")
def delete_product_endpoint(
    product_id: int,
):
    deleted = delete_product(product_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Товар не найден",
        )

    invalidate_cache_safely(product_id)

    return {
        "message": "Товар удалён",
        "id": product_id,
    }


def test_api():
    with TestClient(app) as client:
        response = client.get("/products")
        assert response.status_code == 200
        print("GET /products: OK")

        response = client.get("/products?limit=5&offset=0")
        assert response.status_code == 200

        data = response.json()

        assert "total" in data
        assert "products" in data

        print("GET /products с пагинацией: OK")

        response = client.get("/products/999999")
        assert response.status_code == 404

        print("GET отсутствующего товара: OK")

        response = client.put(
            "/products/999999",
            json={
                "name": "Test",
                "price": "1000.00",
                "stock": 100,
            },
        )
        assert response.status_code == 404

        print("PUT отсутствующего товара: OK")

        response = client.delete("/products/999999")
        assert response.status_code == 404

        print("DELETE отсутствующего товара: OK")

        print("Все тесты выполнены")


def write_log_safely(log_data):
    try:
        save_log(log_data)
    except Exception as e:
        print("Не удалось записать лог для MongoDB", e)


if __name__ == "__main__":
    test_api()
