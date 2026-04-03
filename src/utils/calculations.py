# расчет скидки
def calculate_discount(price, discount_rate):
    return price * discount_rate

# расчет доставки
def calculate_delivery(weight, base_cost=100):
    return base_cost + weight * 10

# итоговая стоимость
def calculate_final_price(price, discount, delivery):
    return price - discount + delivery