from src.models.order import Order
from src.services.order_validator import OrderValidator


class OrderFactory:
    @staticmethod
    def create_order(order_id, user, products):
        order = Order(order_id, user, products)
        OrderValidator.validate(order)
        return order

    @classmethod
    def create_order_from_dict(cls, data):
        return cls.create_order(data["order_id"], data["user"], data["products"])
