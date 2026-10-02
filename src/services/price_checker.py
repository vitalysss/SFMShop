import asyncio


async def find_best_price(product_id: int, suppliers: list):
    tasks = [supplier.get_price(product_id) for supplier in suppliers]

    results = await asyncio.gather(
        *tasks,
        return_exceptions=True,
    )

    prices = [result for result in results if isinstance(result, (int, float))]

    if not prices:
        return None

    return min(prices)
