from abc import ABC, abstractmethod


class Database(ABC):
    @abstractmethod
    def save(self, order):
        pass


class PostgreSQLDatabase(Database):
    def save(self, order):
        print(f"Заказ {order.order_id} сохранён в PostgreSQL ")
