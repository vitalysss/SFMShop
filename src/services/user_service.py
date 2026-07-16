from abc import ABC, abstractmethod
from src.services.order_calculator import OrderCalculator


class UserValidator:
    @staticmethod
    def validate(user):
        if not user.name:
            raise ValueError("Имя не может быть пустым")

        if "@" not in user.email:
            raise ValueError("Email должен содержать @")

        if user.age < 18:
            raise ValueError("Пользователь должен быть старше 18 лет")

        if user.balance < 0:
            raise ValueError("Баланс не может быть отрицательным")

        return True


class UserCalculator:
    @staticmethod
    def calculate_total_spent(user):
        total = 0
        for order in user.orders:
            total += OrderCalculator.calculate_total(order)
        return total


class UserDiscountStrategy(ABC):
    @abstractmethod
    def apply(self, balance):
        pass


class PercentBalanceDiscount(UserDiscountStrategy):
    def __init__(self, percent):
        self.percent = percent

    def apply(self, balance):
        return balance * (1 + self.percent / 100)


class FixedBalanceDiscount(UserDiscountStrategy):
    def __init__(self, amount):
        self.amount = amount

    def apply(self, balance):
        return balance + self.amount


class NotificationService(ABC):
    @abstractmethod
    def send(self, user):
        pass


class EmailNotificationService(NotificationService):
    def send(self, user):
        print(f"Отправка email на {user.email}: Добро пожаловать, {user.name}!")


class Database(ABC):
    @abstractmethod
    def save(self, user):
        pass


class MySQLDatabase(Database):
    def save(self, user):
        print(f"Сохранение пользователя {user.user_id} в MySQL")


class UserService:
    def __init__(self, notification_service, database):
        self.notification_service = notification_service
        self.database = database

    def register_user(self, user):
        UserValidator.validate(user)
        self.notification_service.send(user)
        self.database.save(user)
        return True

    def apply_discount(self, user, discount):
        user.balance = discount.apply(user.balance)
        return user.balance

    def generate_report(self, user):
        total_spent = UserCalculator.calculate_total_spent(user)

        report = f"Пользователь: {user.name}\n"
        report += f"Email: {user.email}\n"
        report += f"Всего заказов: {len(user.orders)}\n"
        report += f"Потрачено: {total_spent}\n"

        print(report)
        return report
