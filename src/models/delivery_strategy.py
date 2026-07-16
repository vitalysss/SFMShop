from abc import ABC, abstractmethod


class DeliveryStrategy(ABC):
    """Абстрактный класс доставки"""

    @abstractmethod
    def calculate_cost(self, distance: float) -> float:
        pass


class StandardDelivery(DeliveryStrategy):
    def calculate_cost(self, distance: float) -> float:
        return distance * 10


class ExpressDelivery(DeliveryStrategy):
    def calculate_cost(self, distance: float) -> float:
        return distance * 20


def process_delivery(delivery: DeliveryStrategy, distance: float) -> float:
    return delivery.calculate_cost(distance)
