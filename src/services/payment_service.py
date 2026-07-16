from abc import ABC, abstractmethod


class PaymentValidator:
    def validate(self, payment):
        if payment.amount <= 0:
            raise ValueError("Сумма оплаты не может быть нулевой или отрицательной")
        return True


class PaymentRepository(ABC):
    @abstractmethod
    def save(self, payment):
        pass


class MySQLPaymentRepository(PaymentRepository):
    def save(self, payment):
        print(f"Сохранение платежа {payment.order_id} в MySQL")


class NotificationService(ABC):
    @abstractmethod
    def send(self, payment):
        pass


class EmailNotificationService(NotificationService):
    def send(self, payment):
        print(f"Отправка email о платеже: {payment.order_id}")


class PaymentProcessor:
    def __init__(self, payment_method, validator, repository, notification_service):
        self.payment_method = payment_method
        self.validator = validator
        self.repository = repository
        self.notification_service = notification_service

    def process_payment(self, payment):
        self.validator.validate(payment)

        result = self.payment_method.process(payment)

        if result:
            payment.status = "completed"
        else:
            payment.status = "failed"
            raise ValueError("Ошибка обработки платежа")

        self.repository.save(payment)
        self.notification_service.send(payment)

        return payment.status
