from src.models.exceptions import NegativePriceError, InsufficientStockError, ValidationError


class Product:
    def __init__(self, name, price, quantity):
        self.name = name
        self.set_price(price)
        self.quantity = quantity

    def sell(self, amount):
        if self.quantity < amount:
            raise InsufficientStockError(
                f"Товара недостаточно. На складе: {self.quantity}, требуется {amount}"
            )

        self.quantity -= amount

    def set_price(self, price):
        if price < 0:
            raise ValidationError("Цена не может быть отрицательной")
        self.price = price

    def get_total_price(self):
        return self.price * self.quantity

    def get_category(self):
        if self.price < 1500:
            return "Бюджетный"
        return "Премиальный"

    def __str__(self):
        return f"Товар: {self.name}, Цена: {self.price} руб. Количество: {self.quantity} "

    def __repr__(self):
        return f"Product('{self.name}', {self.price}, {self.quantity})"

    def __lt__(self, other):
        if not isinstance(other, Product):
            return NotImplemented
        return self.price < other.price

    def __eq__(self, other):
        if not isinstance(other, Product):
            return False
        return self.name == other.name and self.price == other.price
