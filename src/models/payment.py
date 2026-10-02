from abc import ABC, abstractmethod

from src.models.mixins import LoggableMixin, SerializableMixin


class Payment(ABC):
    @abstractmethod
    def process(self):
        pass


class CardPayment(LoggableMixin, SerializableMixin, Payment):
    def __init__(self, amount):
        super().__init__()
        self.amount = amount
        self.log(f"Создан платёж {amount}")

    def process(self):
        self.log("Обработка платежа картой")
        return True

    def to_json(self):
        return {"type": "CardPayment", "amount": self.amount}


class PaymentMethod(ABC):
    @abstractmethod
    def process(self, payment) -> bool:
        pass


class CardPaymentMethod(PaymentMethod):
    def process(self, payment) -> bool:
        if payment.amount > 10000:
            fee_percent = 2
        else:
            fee_percent = 3

        total_amount = payment.amount * (1 + fee_percent / 100)
        print(f"Оплата картой на сумму: {total_amount}")
        return True


class PayPalPaymentMethod(PaymentMethod):
    def process(self, payment) -> bool:
        total_amount = payment.amount * (1 + 3.5 / 100)
        print(f"Оплата PayPal на сумму: {total_amount}")
        return True


class BankTransferPaymentMethod(PaymentMethod):
    def process(self, payment) -> bool:
        total_amount = payment.amount + 50
        print(f"Оплата банковским переводом: {total_amount}")
        return True
