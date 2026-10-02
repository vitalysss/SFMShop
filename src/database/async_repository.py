import asyncpg


class ProductRepository:
    def __init__(self, pool: asyncpg.Pool):
        self.pool = pool

    async def get_by_id(self, product_id: int) -> dict | None:
        async with self.pool.acquire() as conn:
            product = await conn.fetchrow(
                """
                SELECT id, name, price, stock
                FROM products
                WHERE id = $1
                """,
                product_id,
            )

            if product is None:
                return None

            return dict(product)

    async def list_products(self, limit: int = 20, offset: int = 0) -> list[dict]:
        async with self.pool.acquire() as conn:
            products = await conn.fetch(
                """
                SELECT id, name, price, stock
                FROM products
                ORDER BY id
                LIMIT $1 OFFSET $2
                """,
                limit,
                offset,
            )

            return [dict(product) for product in products]

    async def create(self, name: str, price: float, stock: int = 0) -> int:
        async with self.pool.acquire() as conn:
            product_id = await conn.fetchval(
                """
                INSERT INTO products (name, price, stock)
                VALUES ($1, $2, $3)
                RETURNING id
                """,
                name,
                price,
                stock,
            )

            return product_id

    async def update_price(self, product_id: int, new_price: float) -> bool:
        async with self.pool.acquire() as conn:
            status = await conn.execute(
                """
                UPDATE products
                SET price = $1
                WHERE id = $2
                """,
                new_price,
                product_id,
            )

        return status == "UPDATE 1"

    async def delete(self, product_id: int) -> bool:
        async with self.pool.acquire() as conn:
            status = await conn.execute(
                """
                DELETE FROM products
                WHERE id = $1
                """,
                product_id,
            )

        return status == "DELETE 1"
