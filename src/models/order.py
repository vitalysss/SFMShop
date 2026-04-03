from src.models.exceptions import InvalidOrderError, BusinessLogicError
from src.models.product import Product

class Order:
    def __init__(self, user,products):
        self.user = user
        self.products = []
        if not products:
            raise BusinessLogicError("Заказ не может быть пустым")
        for product in products:
            self.add_product(product)

    def add_product(self, product):
        if not isinstance(product, Product):
            raise InvalidOrderError("Товар должен быть объектом класса Product")
        self.products.append(product)



    def calculate_total(self):
        total = 0
        for product in self.products:
            total += product.get_total_price()
        return total

    def __str__(self):
        total = self.calculate_total()
        return f"Заказ пользователя {self.user.name} на сумму {total} руб."
