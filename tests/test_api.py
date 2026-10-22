from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.api.auth import get_current_user
from src.api.dependencies import get_db
from src.api.main import app


def override_current_user():
    return SimpleNamespace(
        user_id=1,
        email="test@example.com",
    )


app.dependency_overrides[get_current_user] = override_current_user

client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@patch("src.api.routes.products.get_cached_products")
def test_get_products(mock_get_cached):
    mock_get_cached.return_value = [
        {
            "id": 1,
            "name": "Keyboard",
            "price": "1000.00",
            "stock": 10,
        },
        {
            "id": 2,
            "name": "Mouse",
            "price": "500.00",
            "stock": 20,
        },
        {
            "id": 3,
            "name": "Monitor",
            "price": "15000.00",
            "stock": 5,
        },
    ]

    response = client.get("/products")

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 3
    assert len(data["products"]) == 3
    assert data["products"][0]["name"] == "Keyboard"

    mock_get_cached.assert_called_once()


@patch("src.api.routes.orders.publish_order_tasks")
@patch("src.api.routes.orders.write_log_safely")
@patch("src.api.routes.orders.invalidate_cache_safely")
@patch("src.api.routes.orders.create_order")
def test_create_order(
    mock_create_order,
    mock_invalidate_cache,
    mock_write_log,
    mock_publish_tasks,
):
    mock_create_order.return_value = SimpleNamespace(
        id=10,
        user_id=1,
        total=Decimal("2000.00"),
        status="pending",
    )

    response = client.post(
        "/orders",
        json={
            "product_id": 2,
            "quantity": 1,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 10
    assert data["user_id"] == 1
    assert data["product_id"] == 2
    assert data["quantity"] == 1
    assert data["status"] == "pending"
    assert data["total"] == "2000.00"

    mock_create_order.assert_called_once_with(
        user_id=1,
        product_id=2,
        quantity=1,
    )


def test_create_order_rejects_user_id_from_request():
    response = client.post(
        "/orders",
        json={
            "user_id": 999,
            "product_id": 2,
            "quantity": 1,
        },
    )

    assert response.status_code == 422


@pytest.fixture(autouse=True)
def clear_database_override():
    yield
    app.dependency_overrides.pop(get_db, None)


def override_database(connection):
    async def _override():
        yield connection

    app.dependency_overrides[get_db] = _override


@patch(
    "src.api.routes.auth.create_access_token",
    return_value="test-token",
)
@patch(
    "src.api.routes.auth.verify_password",
    return_value=True,
)
def test_login_success(
    mock_verify_password,
    mock_create_token,
):
    connection = SimpleNamespace(
        fetchrow=AsyncMock(
            return_value={
                "id": 1,
                "email": "test@example.com",
                "password_hash": "hashed-password",
            }
        )
    )
    override_database(connection)

    response = client.post(
        "/api/v1/login",
        json={
            "email": "test@example.com",
            "password": "password",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "access_token": "test-token",
        "token_type": "bearer",
    }

    mock_verify_password.assert_called_once_with(
        "password",
        "hashed-password",
    )
    mock_create_token.assert_called_once_with(
        user_id=1,
        email="test@example.com",
    )


def test_login_unknown_user():
    connection = SimpleNamespace(fetchrow=AsyncMock(return_value=None))
    override_database(connection)

    response = client.post(
        "/api/v1/login",
        json={
            "email": "missing@example.com",
            "password": "password",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == ("Неверный email или пароль")


@patch(
    "src.api.routes.auth.verify_password",
    return_value=False,
)
def test_login_wrong_password(mock_verify_password):
    connection = SimpleNamespace(
        fetchrow=AsyncMock(
            return_value={
                "id": 1,
                "email": "test@example.com",
                "password_hash": "hashed-password",
            }
        )
    )
    override_database(connection)

    response = client.post(
        "/api/v1/login",
        json={
            "email": "test@example.com",
            "password": "wrong",
        },
    )

    assert response.status_code == 401
    mock_verify_password.assert_called_once()


@patch(
    "src.api.routes.products.invalidate_cache_safely",
)
@patch(
    "src.api.routes.products.write_log_safely",
)
def test_create_product(
    mock_write_log,
    mock_invalidate_cache,
):
    connection = SimpleNamespace(
        fetchrow=AsyncMock(
            return_value={
                "id": 5,
                "name": "Keyboard",
                "price": Decimal("2000.00"),
                "stock": 10,
            }
        )
    )
    override_database(connection)

    response = client.post(
        "/products",
        json={
            "name": "Keyboard",
            "price": "2000.00",
            "stock": 10,
        },
    )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 5
    assert data["name"] == "Keyboard"
    assert data["stock"] == 10

    mock_invalidate_cache.assert_called_once_with(5)
    mock_write_log.assert_called_once()


@patch(
    "src.api.routes.products.get_cached_product",
)
def test_get_product(mock_get_cached_product):
    mock_get_cached_product.return_value = {
        "id": 1,
        "name": "Mouse",
        "price": "1000.00",
        "stock": 5,
    }

    response = client.get("/products/1")

    assert response.status_code == 200
    assert response.json()["name"] == "Mouse"
    mock_get_cached_product.assert_called_once_with(1)


@patch(
    "src.api.routes.products.get_cached_product",
    return_value=None,
)
def test_get_product_not_found(mock_get_cached_product):
    response = client.get("/products/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Товар не найден"
    mock_get_cached_product.assert_called_once_with(999)


@patch(
    "src.api.routes.products.invalidate_cache_safely",
)
@patch(
    "src.api.routes.products.update_product",
)
def test_update_product(
    mock_update_product,
    mock_invalidate_cache,
):
    mock_update_product.return_value = SimpleNamespace(
        id=1,
        name="Updated Mouse",
        price=Decimal("1200.00"),
        stock=7,
    )

    response = client.put(
        "/products/1",
        json={
            "name": "Updated Mouse",
            "price": "1200.00",
            "stock": 7,
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "Updated Mouse",
        "price": "1200.00",
        "stock": 7,
    }

    mock_invalidate_cache.assert_called_once_with(1)


@patch(
    "src.api.routes.products.update_product",
    return_value=None,
)
def test_update_product_not_found(mock_update_product):
    response = client.put(
        "/products/999",
        json={
            "name": "Missing Product",
            "price": "1200.00",
            "stock": 7,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Товар не найден"


@patch(
    "src.api.routes.products.invalidate_cache_safely",
)
@patch(
    "src.api.routes.products.delete_product",
    return_value=True,
)
def test_delete_product(
    mock_delete_product,
    mock_invalidate_cache,
):
    response = client.delete("/products/1")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Товар удалён",
        "id": 1,
    }

    mock_delete_product.assert_called_once_with(1)
    mock_invalidate_cache.assert_called_once_with(1)


@patch(
    "src.api.routes.products.delete_product",
    return_value=False,
)
def test_delete_product_not_found(mock_delete_product):
    response = client.delete("/products/999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Товар не найден"


class FakeAcquire:
    def __init__(self, connection):
        self.connection = connection

    async def __aenter__(self):
        return self.connection

    async def __aexit__(
        self,
        exc_type,
        exc_value,
        traceback,
    ):
        return False


class FakePool:
    def __init__(self, connection):
        self.connection = connection

    def acquire(self):
        return FakeAcquire(self.connection)


@patch(
    "src.api.routes.products.get_cached_products",
)
def test_get_products_with_filters_and_sorting(
    mock_get_cached,
):
    mock_get_cached.return_value = [
        {
            "id": 1,
            "name": "Mouse",
            "price": "500.00",
            "stock": 10,
        },
        {
            "id": 2,
            "name": "Keyboard",
            "price": "2000.00",
            "stock": 5,
        },
        {
            "id": 3,
            "name": "Monitor",
            "price": "15000.00",
            "stock": 2,
        },
    ]

    response = client.get(
        "/products?min_price=500&max_price=3000&sort_by=price&sort_order=desc&limit=1"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 2
    assert len(data["products"]) == 1
    assert data["products"][0]["name"] == "Keyboard"
    assert response.headers["Cache-Control"] == "max-age=3600"


def test_get_products_rejects_invalid_price_range():
    response = client.get("/products?min_price=5000&max_price=1000")

    assert response.status_code == 422
    assert response.json()["detail"] == ("min_price не может быть больше max_price")


@patch(
    "src.api.routes.orders.write_log_safely",
)
@patch(
    "src.api.routes.orders.create_order",
    return_value=None,
)
def test_create_order_failure(
    mock_create_order,
    mock_write_log,
):
    response = client.post(
        "/orders",
        json={
            "product_id": 999,
            "quantity": 1,
        },
    )

    assert response.status_code == 400
    assert response.json()["detail"].startswith("Не удалось создать заказ")

    mock_create_order.assert_called_once()
    mock_write_log.assert_called_once()


@patch(
    "src.api.routes.orders.process_orders_async",
    new_callable=AsyncMock,
)
def test_process_orders_partial_success(
    mock_process_orders,
):
    mock_process_orders.return_value = [
        {
            "order_id": 1,
            "status": "completed",
        },
        {
            "order_id": 2,
            "status": "failed",
        },
    ]

    response = client.post(
        "/orders/process",
        json={"order_ids": [1, 2]},
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": "partial_success",
        "processed": 2,
        "successful": 1,
        "failed": 1,
        "results": [
            {
                "order_id": 1,
                "status": "completed",
            },
            {
                "order_id": 2,
                "status": "failed",
            },
        ],
    }

    mock_process_orders.assert_awaited_once_with([1, 2])


@patch(
    "src.api.routes.orders.process_orders_async",
    new_callable=AsyncMock,
)
def test_process_orders_success(mock_process_orders):
    mock_process_orders.return_value = [
        {
            "order_id": 1,
            "status": "completed",
        }
    ]

    response = client.post(
        "/orders/process",
        json={"order_ids": [1]},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["successful"] == 1
    assert response.json()["failed"] == 0


@patch(
    "src.api.routes.orders.process_orders_async",
    new_callable=AsyncMock,
)
def test_process_orders_background(mock_process_orders):
    mock_process_orders.return_value = []

    response = client.post(
        "/orders/process-background",
        json={"order_ids": [1, 2, 3]},
    )

    assert response.status_code == 202
    assert response.json() == {
        "status": "accepted",
        "message": "Обработка заказов запущена в фоне",
        "orders_count": 3,
    }

    mock_process_orders.assert_awaited_once_with([1, 2, 3])


def test_get_products_v1():
    connection = SimpleNamespace(
        fetch=AsyncMock(
            return_value=[
                {
                    "id": 1,
                    "name": "Mouse",
                    "stock": 5,
                },
                {
                    "id": 2,
                    "name": "Keyboard",
                    "stock": 10,
                },
            ]
        )
    )
    app.state.db_pool = FakePool(connection)

    response = client.get("/api/v1/products")

    assert response.status_code == 200
    assert response.json()["products"] == [
        {
            "id": 1,
            "name": "Mouse",
            "stock": 5,
        },
        {
            "id": 2,
            "name": "Keyboard",
            "stock": 10,
        },
    ]


def test_create_product_v1():
    connection = SimpleNamespace(fetchrow=AsyncMock(return_value={"id": 25}))
    app.state.db_pool = FakePool(connection)

    response = client.post(
        "/api/v1/products",
        json={
            "name": "Monitor",
            "price": "15000.00",
            "stock": 3,
        },
    )

    assert response.status_code == 201
    assert response.json() == {
        "id": 25,
        "status": "created",
    }


def test_get_products_v2():
    response = client.get("/api/v2/products")

    assert response.status_code == 200
    assert response.json() == {
        "data": [],
        "metadata": {
            "version": "2.0",
        },
    }


@patch(
    "src.api.routes.external.ExternalAPIService.get_exchange_rate",
    new_callable=AsyncMock,
)
def test_get_exchange_rate(mock_get_exchange_rate):
    mock_get_exchange_rate.return_value = 0.91
    app.state.http_client = SimpleNamespace()

    response = client.get("/api/v1/exchange-rate?base=USD&target=EUR")

    assert response.status_code == 200
    assert response.json() == {
        "base": "USD",
        "target": "EUR",
        "rate": 0.91,
    }

    mock_get_exchange_rate.assert_awaited_once_with(
        "USD",
        "EUR",
    )


def test_get_product_full_from_cache():
    connection = SimpleNamespace(
        fetchrow=AsyncMock(
            return_value={
                "id": 1,
                "name": "Mouse",
                "price": Decimal("1000.00"),
                "stock": 5,
            }
        )
    )
    override_database(connection)

    app.state.redis = SimpleNamespace(
        get=AsyncMock(return_value='[{"rating": 5}]'),
        incr=AsyncMock(return_value=7),
    )
    app.state.http_client = SimpleNamespace()

    response = client.get("/api/products/1/full")

    assert response.status_code == 200
    assert response.json() == {
        "product": {
            "id": 1,
            "name": "Mouse",
            "price": 1000.0,
            "stock": 5,
        },
        "reviews": [{"rating": 5}],
        "views": 7,
    }


def test_admin_page():
    response = client.get("/admin")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
