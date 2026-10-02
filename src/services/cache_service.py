import json
from uuid import uuid4

import redis

from src.config import REDIS_URL
from src.database.queries_orm import get_all_products, get_product

redis_client = redis.Redis.from_url(
    REDIS_URL,
    decode_responses=True,
)


def get_cached_products():
    cache_key = "products:all"

    try:
        cached = redis_client.get(cache_key)
    except redis.RedisError:
        cached = None

    if cached:
        print("HIT")
        return json.loads(cached)

    print("MISS")
    products = get_all_products()
    products_data = [product_to_dict(product) for product in products]

    try:
        redis_client.setex(
            cache_key,
            3600,
            json.dumps(products_data),
        )
    except redis.RedisError:
        pass

    return products_data


def product_to_dict(product):
    return {
        "id": product.id,
        "name": product.name,
        "price": str(product.price),
        "stock": product.stock,
    }


def invalidate_products_cache():
    try:
        redis_client.delete("products:all")
    except redis.RedisError:
        pass


def get_cached_product(product_id):
    cache_key = f"product:{product_id}"

    try:
        cached = redis_client.get(cache_key)
    except redis.RedisError:
        cached = None

    if cached:
        print("HIT")
        return json.loads(cached)

    print("MISS")

    product = get_product(product_id)

    if product is None:
        return None

    product_data = product_to_dict(product)

    try:
        redis_client.setex(
            cache_key,
            3600,
            json.dumps(product_data),
        )
    except redis.RedisError:
        pass

    return product_data


def invalidate_product_cache(product_id):
    try:
        redis_client.delete(
            f"product:{product_id}",
        )
        redis_client.delete("products:all")
    except redis.RedisError:
        pass


def create_user_session(user_id):
    session_token = str(uuid4())

    session_key = f"session:{session_token}"

    session_data = {"user_id": user_id}

    redis_client.setex(session_key, 86400, json.dumps(session_data))

    return session_token


def get_user_session(session_token):
    session_key = f"session:{session_token}"

    cached = redis_client.get(session_key)

    if cached is None:
        return None

    return json.loads(cached)


def delete_user_session(session_token):
    session_key = f"session:{session_token}"

    redis_client.delete(session_key)
