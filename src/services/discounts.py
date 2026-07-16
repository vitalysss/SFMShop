from abc import abstractmethod, ABC


class DiscountStrategy(ABC):
    @abstractmethod
    def apply(self, price):
        pass


class PercentDiscount(DiscountStrategy):
    def __init__(self, percent):
        self.percent = percent

    def apply(self, price):
        return price * (1 - self.percent / 100)


class FixedDiscount(DiscountStrategy):
    def __init__(self, amount):
        self.amount = amount

    def apply(self, price):
        return max(0, price - self.amount)
