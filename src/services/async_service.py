import asyncio
import time
from typing import Any

import aiohttp

from src.models.order import Order
from src.models.product import Product
from src.models.user import User
from src.services.log_service import save_log

PROCESSING_DELAY = 0.1


def build_demo_order(order_id: int) -> Order:
    user = User(
        user_id=order_id,
        name=f"Пользователь {order_id}",
        email=f"user{order_id}@example.com",
        age=25,
        balance=100000,
    )

    products = [
        Product(
            name=f"Товар {order_id}",
            price=1000 + order_id,
            quantity=1,
        )
    ]

    return Order(
        order_id=order_id,
        user=user,
        products=products,
    )


async def log_order_error(order_id: int, error: Exception) -> None:
    log_data = {
        "event_type": "async_order_failed",
        "message": str(error),
        "status_code": 500,
        "order_id": order_id,
    }

    try:
        await asyncio.to_thread(save_log, log_data)

    except Exception as log_error:
        print(
            "Не удалось записать ошибку в MongoDB:",
            log_error,
        )


async def process_order(order_id: int) -> dict[str, Any]:
    status = "processing"

    try:
        if order_id <= 0:
            raise ValueError("Идентификатор заказа должен быть положительным")

        await asyncio.sleep(PROCESSING_DELAY)

        order = build_demo_order(order_id)

        total = sum(product.price * product.quantity for product in order.products)

        status = "completed"

        return {
            "order_id": order_id,
            "user": order.user.name,
            "total": total,
            "status": status,
            "message": f"Заказ {order_id} обработан",
        }

    except Exception as error:
        status = "failed"

        await log_order_error(order_id, error)

        return {
            "order_id": order_id,
            "status": status,
            "error": str(error),
        }


async def process_orders_async(order_ids: list[int]) -> list[dict[str, Any]]:
    tasks = [process_order(order_id) for order_id in order_ids]

    results = await asyncio.gather(*tasks)

    return results


def process_orders_sync(order_ids: list[int]) -> list[str]:
    results = []

    for order_id in order_ids:
        time.sleep(PROCESSING_DELAY)
        results.append(f"Заказ {order_id} обработан")

    return results


async def compare_performance() -> None:
    order_ids = list(range(1, 101))

    sync_start = time.time()
    sync_results = process_orders_sync(order_ids)
    sync_time = time.time() - sync_start

    async_start = time.time()
    async_results = await process_orders_async(order_ids)
    async_time = time.time() - async_start

    print(f"Синхронная обработка: {sync_time:.2f} сек")

    print(f"Асинхронная обработка: {async_time:.2f} сек")

    print(f"Ускорение: {sync_time / async_time:.2f} раз")

    print(f"Обработано синхронно: {len(sync_results)}")

    print(f"Обработано асинхронно: {len(async_results)}")


async def fetch_order_details_async(
    order_id: int, session: aiohttp.ClientSession
) -> dict[str, Any] | None:
    url = f"https://jsonplaceholder.typicode.com/todos/{order_id}"

    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.json()

    except aiohttp.ClientError as error:
        await log_order_error(order_id, error)
        return None

    except asyncio.TimeoutError as error:
        await log_order_error(order_id, error)
        return None


async def test_http_requests() -> None:
    timeout = aiohttp.ClientTimeout(total=5)

    async with aiohttp.ClientSession(timeout=timeout) as session:
        tasks = [fetch_order_details_async(order_id, session) for order_id in range(1, 6)]

        results = await asyncio.gather(*tasks)

    for result in results:
        print(result)


async def main():
    print("Проверка производительности: ")
    await compare_performance()

    print("\nПроверка HTTP-запросов: ")
    await test_http_requests()


if __name__ == "__main__":
    asyncio.run(main())
