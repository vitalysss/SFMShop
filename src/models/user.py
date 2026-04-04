from src.models.exceptions import ValidationError


class User:
    def __init__(self, name, email):
        self.name = name
        self.set_email(email)

    def set_email(self, email):
        if '@' not in email or '.' not in email:
            raise ValidationError('Неверный формат email')
        self._email = email