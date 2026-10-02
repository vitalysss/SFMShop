import asyncio


async def validate_order(order_id: int):
    await asyncio.sleep(1)
    return {"order_id": order_id, "validated": True}


async def reserve_product(order_id: int):
    await asyncio.sleep(2)
    return {"product_reserved": True}


async def verify_address(order_id: int):
    await asyncio.sleep(1)
    return {"address_verified": True}


async def process_order(order_id: int):
    failed = False
    try:
        async with asyncio.TaskGroup() as group:
            validation_task = group.create_task(validate_order(order_id))

            reservation_task = group.create_task(reserve_product(order_id))

            address_task = group.create_task(verify_address(order_id))

    except* Exception as errors:
        print(f"Ошибка обработки заказа: {errors}")
        failed = True

    if failed:
        return None

    result = {}

    result.update(validation_task.result())
    result.update(reservation_task.result())
    result.update(address_task.result())

    result["status"] = "ready"

    return result


async def main():
    result = await process_order(10)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
