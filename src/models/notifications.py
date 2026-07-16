from abc import ABC, abstractmethod


class Notification(ABC):
    @abstractmethod
    def send(self, message: str):
        pass


class EmailNotification(Notification):
    def send(self, message: str):
        print(f"Отправка email: {message}")


class SMSNotification(Notification):
    def send(self, message: str):
        print(f"Отправка SMS: {message}")


def send_notifications(notifications: list[Notification], message: str):
    for notification in notifications:
        notification.send(message)
