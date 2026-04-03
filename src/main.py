from src.utils.order_processor import process_order_file
from src.models.product import Product
from src.models.order import Order
from src.models.user import User
from src.models.payment import Payment, CardPayment, PayPalPayment
from src.models.exceptions import SFMShopException, ValidationError

process_order_file('../data/orders.txt', '../data/processed_orders_report.txt')

"""Демонстрация использования магических методов"""
products = [
    Product('Ноутбук', 50000, 10),
    Product('Мышь', 1500, 20),
    Product('Клавиатура', 3000, 15)
]
print(products[0]) # первый товар
print(repr(products[0])) # repr первого товара
sorted_products = sorted(products)
for product in sorted_products:
    print(product)

"""Демонстрация полиморфизма"""
payments = [
    CardPayment(1000, "1234 5678 9012 3456"),
    PayPalPayment(2000, 'user@paypal.com')
]

for payment in payments:
    print(payment.process_payment())


def process_order_system():
    user = User("Иван", "ivan@test.com")
    product1 = Product("Ноутбук", 50000, 2)
    product2 = Product("Мышь", 1500, 3)
    order = Order(user, [product1, product2])
    total = order.calculate_total()
    print(f"Общая стоимость заказа: {total}")
    payments = [
        CardPayment(1000, "1234 5678 9012 3456"),
        PayPalPayment(2000, "test@paypal.com")
    ]
    for payment in payments:
        print(payment.process_payment())
    sorted_products = sorted([product1, product2])
    for product in sorted_products:
        print(product)
    try:
        product1.set_price(-1000)
    except ValidationError as e:
        print(f"Ошибка валидации: {e}")
    """Демонстрация работы обработки исключений"""
    try:
        bad_user = User("Пётр", "какой-то email")
    except SFMShopException as e:
        print(f"Ошибка: {e}")
    # неправильный продукт
    try:
        bad_product = Product("Ноутбук", -10000, 5)
    except SFMShopException as e:
        print(f"Ошибка: {e}")
    # неправильный заказ
    try:
        bad_order = Order(user, [])
    except SFMShopException as e:
        print(f"Ошибка: {e}")

