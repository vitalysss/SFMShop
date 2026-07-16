from abc import ABC, abstractmethod


class NotificationService(ABC):
    @abstractmethod
    def send(self, order):
        pass


class EmailNotificationService(NotificationService):
    def send(self, order):
        print(f"Отправка email на {order.user.email}")
