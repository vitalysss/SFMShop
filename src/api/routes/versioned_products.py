from fastapi import APIRouter, Request, status

from src.api.schemas import ProductCreate

v1_router = APIRouter(prefix="/api/v1")
v2_router = APIRouter(prefix="/api/v2")


@v1_router.get("/products")
async def get_products_v1(request: Request):
    pool = request.app.state.db_pool

    async with pool.acquire() as conn:
        products = await conn.fetch(
            """
            SELECT id, name, stock
            FROM products
            ORDER BY id
            """
        )

    return {
        "products": [dict(product) for product in products],
    }


@v1_router.post("/products", status_code=status.HTTP_201_CREATED)
async def create_product_v1(product: ProductCreate, request: Request):
    pool = request.app.state.db_pool

    async with pool.acquire() as conn:
        new_product = await conn.fetchrow(
            """
            INSERT INTO products (name, price, stock)
            VALUES ($1, $2, $3)
            RETURNING id
            """,
            product.name,
            product.price,
            product.stock,
        )

    return {
        "id": new_product["id"],
        "status": "created",
    }


@v2_router.get("/products")
async def get_products_v2():
    return {
        "data": [],
        "metadata": {
            "version": "2.0",
        },
    }
