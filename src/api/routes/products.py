import asyncio
import json
from decimal import Decimal
from typing import Literal

import asyncpg
import httpx
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    HTTPException,
    Query,
    Request,
    Response,
    status,
)

from src.api.auth import TokenData, get_current_user
from src.api.dependencies import get_db
from src.api.helpers import invalidate_cache_safely, write_log_safely
from src.api.schemas import ProductCreate, ProductUpdate
from src.database.queries_orm import delete_product, update_product
from src.services.cache_service import (
    get_cached_product,
    get_cached_products,
)

router = APIRouter()


@router.get("/products")
async def get_products(
    response: Response,
    limit: int = Query(default=10, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    min_price: Decimal | None = Query(default=None, ge=0),
    max_price: Decimal | None = Query(default=None, ge=0),
    sort_by: Literal["id", "name", "price"] | None = None,
    sort_order: Literal["asc", "desc"] = "asc",
    current_user: TokenData = Depends(get_current_user),
):
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="min_price не может быть больше max_price",
        )

    products = await asyncio.to_thread(get_cached_products)
    filtered_products = products

    if min_price is not None:
        filtered_products = [
            product for product in filtered_products if Decimal(product["price"]) >= min_price
        ]

    if max_price is not None:
        filtered_products = [
            product for product in filtered_products if Decimal(product["price"]) <= max_price
        ]

    if sort_by is not None:
        reverse = sort_order == "desc"

        if sort_by == "price":
            filtered_products = sorted(
                filtered_products,
                key=lambda product: Decimal(product["price"]),
                reverse=reverse,
            )
        else:
            filtered_products = sorted(
                filtered_products,
                key=lambda product: product[sort_by],
                reverse=reverse,
            )

    response.headers["Cache-Control"] = "max-age=3600"

    return {
        "total": len(filtered_products),
        "limit": limit,
        "offset": offset,
        "products": filtered_products[offset : offset + limit],
    }


@router.post(
    "/products",
    status_code=status.HTTP_201_CREATED,
)
async def create_product_endpoint(
    product_data: ProductCreate,
    background_tasks: BackgroundTasks,
    conn: asyncpg.Connection = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    product = await conn.fetchrow(
        """
        INSERT INTO products (name, price, stock)
        VALUES ($1, $2, $3)
        RETURNING id, name, price, stock
        """,
        product_data.name,
        product_data.price,
        product_data.stock,
    )

    await asyncio.to_thread(
        invalidate_cache_safely,
        product["id"],
    )

    background_tasks.add_task(
        write_log_safely,
        {
            "action": "create_product",
            "product_id": product["id"],
            "user_id": current_user.user_id,
        },
    )

    return dict(product)


@router.get("/products/{product_id}")
async def get_product_endpoint(
    product_id: int,
    current_user: TokenData = Depends(get_current_user),
):
    product = await asyncio.to_thread(
        get_cached_product,
        product_id,
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден",
        )

    return product


@router.get("/api/products/{product_id}/full")
async def get_product_full(
    product_id: int,
    request: Request,
    conn: asyncpg.Connection = Depends(get_db),
    current_user: TokenData = Depends(get_current_user),
):
    redis_client = request.app.state.redis
    http_client = request.app.state.http_client

    async def fetch_product():
        return await conn.fetchrow(
            """
            SELECT id, name, price, stock
            FROM products
            WHERE id = $1
            """,
            product_id,
        )

    async def fetch_reviews():
        cache_key = f"reviews:product:{product_id}"

        try:
            cached = await redis_client.get(cache_key)
        except Exception:
            cached = None

        if cached is not None:
            return json.loads(cached)

        try:
            response = await http_client.get(f"https://api.reviews.sfmshop.ru/product/{product_id}")
            response.raise_for_status()
            reviews = response.json()
        except httpx.HTTPError:
            return []

        try:
            await redis_client.setex(
                cache_key,
                600,
                json.dumps(reviews),
            )
        except Exception:
            pass

        return reviews

    async def fetch_views():
        try:
            return await redis_client.incr(f"views:product:{product_id}")
        except Exception:
            return None

    product, reviews, views = await asyncio.gather(
        fetch_product(),
        fetch_reviews(),
        fetch_views(),
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден",
        )

    return {
        "product": dict(product),
        "reviews": reviews,
        "views": views,
    }


@router.put("/products/{product_id}")
async def update_product_endpoint(
    product_id: int,
    product_data: ProductUpdate,
    current_user: TokenData = Depends(get_current_user),
):
    product = await asyncio.to_thread(
        update_product,
        product_id=product_id,
        name=product_data.name,
        price=product_data.price,
        stock=product_data.stock,
    )

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден",
        )

    await asyncio.to_thread(
        invalidate_cache_safely,
        product_id,
    )

    return {
        "id": product.id,
        "name": product.name,
        "price": str(product.price),
        "stock": product.stock,
    }


@router.delete("/products/{product_id}")
async def delete_product_endpoint(
    product_id: int,
    current_user: TokenData = Depends(get_current_user),
):
    deleted = await asyncio.to_thread(
        delete_product,
        product_id,
    )

    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Товар не найден",
        )

    await asyncio.to_thread(
        invalidate_cache_safely,
        product_id,
    )

    return {
        "message": "Товар удалён",
        "id": product_id,
    }
