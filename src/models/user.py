from src.models.metaclasses import ModelMeta
from src.models.descriptors import PositiveNumber


class User(metaclass=ModelMeta):
    user_id = PositiveNumber("_user_id")
    age = PositiveNumber("_age")
    balance = PositiveNumber("_balance")

    def __init__(self, user_id, name, email, age, balance):
        self.user_id = user_id
        self.name = name
        self.email = email
        self.age = age
        self.balance = balance
        self.orders = []
        self.is_active = True
