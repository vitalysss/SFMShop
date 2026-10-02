from src.database.models import Product


# расчет скидки
def calculate_discount(price, discount_rate):
    return price * discount_rate


# расчет доставки
def calculate_delivery(weight, distance):
    base_price = 100
    weight_price = weight * 10
    distance_price = distance * 5

    return base_price + weight_price + distance_price


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
def find_product_in_dict(products_dict: dict[int, Product], product_id: int) -> Product | None:
    return products_dict.get(product_id)
