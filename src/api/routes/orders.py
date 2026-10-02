import asyncio

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
)

from src.api.auth import TokenData, get_current_user
from src.api.helpers import (
    invalidate_cache_safely,
    write_log_safely,
)
from src.api.schemas import OrderCreate, OrderIdsRequest
from src.database.queries_orm import create_order
from src.services.async_service import process_orders_async
from src.services.log_service import log_service
from src.services.queue_producer import QueueProducer

router = APIRouter()


def publish_order_tasks(
    order_id: int,
    product_id: int,
    quantity: int,
    user_email: str,
):
    producer = QueueProducer()

    try:
        stock_sent = producer.send_order_task(
            order_id,
            "update_stock",
            {
                "items": [
                    {
                        "product_id": product_id,
                        "quantity": quantity,
                    }
                ],
            },
        )

        report_sent = producer.send_order_task(
            order_id,
            "generate_report",
            {},
        )

        email_sent = producer.send_order_task(
            order_id,
            "send_email",
            {
                "user_email": user_email,
            },
        )

        if not stock_sent or not report_sent or not email_sent:
            raise RuntimeError("Не удалось отправить задачи в RabbitMQ")
    finally:
        producer.close()


@router.post("/orders", status_code=201)
async def create_new_order(
    order_data: OrderCreate,
    current_user: TokenData = Depends(get_current_user),
):
    log_service.info(
        "Создание заказа: user_id=%s, product_id=%s, quantity=%s",
        current_user.user_id,
        order_data.product_id,
        order_data.quantity,
    )

    order = await asyncio.to_thread(
        create_order,
        user_id=current_user.user_id,
        product_id=order_data.product_id,
        quantity=order_data.quantity,
    )

    if order is None:
        log_service.warning(
            "Заказ не создан: user_id=%s, product_id=%s",
            current_user.user_id,
            order_data.product_id,
        )

        await asyncio.to_thread(
            write_log_safely,
            {
                "event_type": "order_failed",
                "message": "Не удалось создать заказ",
                "status_code": 400,
                "user_id": current_user.user_id,
                "product_id": order_data.product_id,
                "quantity": order_data.quantity,
            },
        )

        raise HTTPException(
            status_code=400,
            detail=("Не удалось создать заказ. Проверьте пользователя, товар, остаток и баланс."),
        )

    await asyncio.to_thread(
        invalidate_cache_safely,
        order_data.product_id,
    )

    await asyncio.to_thread(
        write_log_safely,
        {
            "event_type": "order_created",
            "message": f"Заказ создан {order.id}",
            "status_code": 201,
            "user_id": order.user_id,
            "product_id": order_data.product_id,
            "quantity": order_data.quantity,
        },
    )

    log_service.info(
        "Заказ создан: order_id=%s, user_id=%s",
        order.id,
        order.user_id,
    )

    await asyncio.to_thread(
        publish_order_tasks,
        order.id,
        order_data.product_id,
        order_data.quantity,
        current_user.email,
    )

    return {
        "id": order.id,
        "user_id": order.user_id,
        "total": str(order.total),
        "status": order.status,
        "quantity": order_data.quantity,
        "product_id": order_data.product_id,
    }


@router.post("/orders/process")
async def process_orders_endpoint(
    request_data: OrderIdsRequest,
    current_user: TokenData = Depends(get_current_user),
):
    try:
        results = await process_orders_async(request_data.order_ids)
    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail="Не удалось обработать заказ",
        ) from error

    successful = 0

    for result in results:
        try:
            if result.get("status") == "completed":
                successful += 1
        except AttributeError as error:
            raise HTTPException(
                status_code=500,
                detail=("Некорректный результат обработки заказа"),
            ) from error

    failed = len(results) - successful

    response_status = "success" if failed == 0 else "partial_success"

    return {
        "status": response_status,
        "processed": len(results),
        "successful": successful,
        "failed": failed,
        "results": results,
    }


@router.post(
    "/orders/process-background",
    status_code=202,
)
async def process_orders_background(
    request_data: OrderIdsRequest,
    background_tasks: BackgroundTasks,
    current_user: TokenData = Depends(get_current_user),
):
    background_tasks.add_task(
        process_orders_async,
        request_data.order_ids.copy(),
    )

    return {
        "status": "accepted",
        "message": "Обработка заказов запущена в фоне",
        "orders_count": len(request_data.order_ids),
    }
