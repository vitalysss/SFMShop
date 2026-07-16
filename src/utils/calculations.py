import time
from src.models.product import Product


# расчет скидки
def calculate_discount(price, discount_rate):
    return price * discount_rate


# расчет доставки
def calculate_delivery(weight, base_cost=100):
    return base_cost + weight * 10


# итоговая стоимость
def calculate_final_price(price, discount, delivery):
    return price - discount + delivery


# медленная функция поиска через списки
def find_product_in_list(products: list[Product], product_id: int) -> Product | None:
    """Поиск в списке (медленный)"""
    for product in products:
        if product.id == product_id:
            return product
    return None


# функция для преобразования продуктов из списка в словарь
def create_products_catalog(products: list[Product]) -> dict[int, Product]:
    return {product.id: product for product in products}


# функция для поиска продуктов в словаре
def find_product_in_dict(
    products_dict: dict[int, Product], product_id: int
) -> Product | None:
    return products_dict.get(product_id)
