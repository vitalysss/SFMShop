from src.models.descriptors import PositiveNumber

from src.models.metaclasses import ModelMeta
from src.models.mixins import LoggableMixin, SerializableMixin


class Order(LoggableMixin, SerializableMixin, metaclass=ModelMeta):
    order_id = PositiveNumber("_order_id")

    def __init__(self, order_id, user, products):
        self.user = user
        self.products = products
        self.order_id = order_id
        self.log(f"Создан заказ: {order_id}")

    def __eq__(self, other):
        if not isinstance(other, Order):
            return False
        return self.order_id == other.order_id

    def __str__(self):
        return f"Заказ {self.order_id} пользователя {self.user.name}"

    def __len__(self):
        return len(self.products)

    def __contains__(self, product):
        if isinstance(product, str):
            return any(
                item == product if isinstance(item, str) else item.name == product
                for item in self.products
            )

        return product in self.products

    def __add__(self, other):
        if not isinstance(other, Order):
            return NotImplemented

        new_products = self.products + other.products
        return Order(self.order_id, self.user, new_products)

    def __lt__(self, other):
        if not isinstance(other, Order):
            return NotImplemented

        return self.order_id < other.order_id
