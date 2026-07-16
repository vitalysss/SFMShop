class OrderCalculator:
    @staticmethod
    def calculate_total(order):
        total = 0
        for product in order.products:
            total += product.price * product.quantity
        return total

    @staticmethod
    def calculate_total_with_discount(order, discount):
        total = OrderCalculator.calculate_total(order)
        final_total = discount.apply(total)
        return final_total
