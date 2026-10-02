from src.services.order_calculator import OrderCalculator
from src.services.order_validator import OrderValidator


class OrderService:
    def __init__(self, notification_service, database):
        self.notification_service = notification_service
        self.database = database

    def process_order(self, order, discount=None):
        OrderValidator.validate(order)
        if discount:
            total = OrderCalculator.calculate_total_with_discount(order, discount)
        else:
            total = OrderCalculator.calculate_total(order)

        self.notification_service.send(order)
        self.database.save(order)
        return total


def validate_order_data(order_data):
    if not order_data.get("user_id"):
        raise ValueError("Нет user_id")

    if not order_data.get("items"):
        raise ValueError("Нет товаров")

    if len(order_data.get("items", [])) == 0:
        raise ValueError("Список товаров пуст")

    for item in order_data["items"]:
        if "price" not in item:
            raise ValueError("Нет цены товара")

        if "quantity" not in item:
            raise ValueError("Нет количества")

        if item["price"] < 0:
            raise ValueError("Цена не может быть отрицательной")

        if item["quantity"] <= 0:
            raise ValueError("Количество должно быть положительным")

    return True


def calculate_order_total(order_data):
    total = 0

    for item in order_data["items"]:
        total += item["price"] * item["quantity"]

    return total


def calculate_discount(total):
    if total > 10000:
        return 0.15

    if total > 5000:
        return 0.10

    if total > 1000:
        return 0.05

    return 0


def get_user_balance(user_id):
    return 100000


def check_user_balance(user_id, final_total):
    user_balance = get_user_balance(user_id)

    if user_balance < final_total:
        raise ValueError("Недостаточно средств")

    return True


def save_order_to_db(user_id, items, final_total):
    print(f"Сохранение заказа пользователя {user_id} на сумму {final_total}")
    return 1


def create_order(order_data, final_total):
    order_id = save_order_to_db(order_data["user_id"], order_data["items"], final_total)

    return order_id


def get_user_email(user_id):
    return "vitaly@test.com"


def send_email(email, message):
    print(f"Отправка на email {email}: {message}")


def notify_user(user_id, order_id, final_total):
    user_email = get_user_email(user_id)
    send_email(user_email, f"Заказ #{order_id} оформлен на сумму {final_total}")
    return True


def process_order(order_data):
    validate_order_data(order_data)

    total = calculate_order_total(order_data)
    discount = calculate_discount(total)
    final_total = total * (1 - discount)

    check_user_balance(order_data["user_id"], final_total)

    order_id = create_order(order_data, final_total)

    notify_user(order_data["user_id"], order_id, final_total)

    print(f"Заказ {order_id} обработан: пользователь {order_data['user_id']}, сумма {final_total}")

    return {"order_id": order_id, "total": final_total, "discount": discount}
