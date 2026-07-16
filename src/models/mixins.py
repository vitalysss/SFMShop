class LoggableMixin:
    def log(self, message):
        class_name = self.__class__.__name__
        print(f"[{class_name}] {message}")


class ValidatableMixin:
    def validate(self):
        return True

    def is_valid(self):
        try:
            self.validate()
            return True
        except ValueError:
            return False


class SerializableMixin:
    def to_json(self):
        class_name = self.__class__.__name__
        return {"class": class_name, "data": self.__dict__}
