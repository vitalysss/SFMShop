import redis
import os
import json
from uuid import uuid4
from src.database.queries_orm import get_all_products, get_product
from dotenv import load_dotenv

load_dotenv()

redis_client = redis.Redis(
    host=os.getenv(
        "REDIS_HOST",
        "127.0.0.1",
    ),
    port=int(
        os.getenv(
            "REDIS_PORT",
            "6379",
        )
    ),
    db=0,
    decode_responses=True,
)


def get_cached_products():
    cache_key = "products:all"

    cached = redis_client.get(cache_key)

    if cached:
        print("HIT")
        return json.loads(cached)

    print("MISS")
    products = get_all_products()
    products_data = [product_to_dict(product) for product in products]
    redis_client.setex(cache_key, 3600, json.dumps(products_data))

    return products_data


def product_to_dict(product):
    return {
        "id": product.id,
        "name": product.name,
        "price": str(product.price),
        "stock": product.stock,
    }


def invalidate_products_cache():
    redis_client.delete("products:all")


def get_cached_product(product_id):
    cache_key = f"product:{product_id}"

    cached = redis_client.get(cache_key)

    if cached:
        print("HIT")
        return json.loads(cached)

    print("MISS")

    product = get_product(product_id)

    if product is None:
        return None

    product_data = product_to_dict(product)

    redis_client.setex(cache_key, 3600, json.dumps(product_data))

    return product_data


def invalidate_product_cache(product_id):
    redis_client.delete(f"product:{product_id}")
    redis_client.delete("products:all")


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
