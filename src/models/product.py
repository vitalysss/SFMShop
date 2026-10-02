from src.models.descriptors import CachedProperty, PositiveNumber
from src.models.metaclasses import ModelMeta
from src.models.mixins import LoggableMixin, SerializableMixin, ValidatableMixin
from src.services.discounts import DiscountStrategy


class Product(LoggableMixin, ValidatableMixin, SerializableMixin, metaclass=ModelMeta):
    price = PositiveNumber("_price")
    quantity = PositiveNumber("_quantity")

    def __init__(self, name: str, price: float, quantity: int):
        self.name = name
        self.price = price
        self.quantity = quantity

        self.validate()
        self.log(f"Создан товар: {self.name}")

    def validate(self):
        if not self.name:
            raise ValueError("Название товара не может быть пустым")
        return True

    def calculate_price(self, discount: DiscountStrategy) -> float:
        return discount.apply(self.price)

    @CachedProperty
    def total_value(self):
        print("Вычисление")
        return self.price * self.quantity

    @classmethod
    def from_dict(cls, data):
        return cls(name=data["name"], price=data["price"], quantity=data["quantity"])
