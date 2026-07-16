class OrderValidator:
    @staticmethod
    def validate(order):
        if not order.user:
            raise ValueError("У заказа должен быть пользователь")

        if not order.products:
            raise ValueError("Заказ не может быть пустым")

        for product in order.products:
            if product.quantity <= 0:
                raise ValueError("Количество товара должно быть больше 0")

        return True
