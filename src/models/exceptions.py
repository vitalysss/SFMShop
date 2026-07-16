class SFMShopException(Exception):
    """Базовый класс исключений"""

    pass


class ValidationError(SFMShopException):
    """Ошибки валидации"""

    pass


class BusinessLogicError(SFMShopException):
    """Ошибки бизнес логики"""

    pass


class DatabaseError(SFMShopException):
    """Ошибки баз данных"""

    pass


class NegativePriceError(ValidationError):
    """Цена не может быть отрицательной"""

    pass


class InsufficientStockError(BusinessLogicError):
    """Недостаточно товара"""

    pass


class InvalidOrderError(BusinessLogicError):
    """Невалидный заказ"""

    pass
