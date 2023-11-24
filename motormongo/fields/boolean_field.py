from motormongo.fields.field import Field


class BooleanField(Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def __set__(self, obj, value):
        if value is not None and not isinstance(value, bool):
            raise ValueError(f"Value for {self.name} must be a boolean")
        super().__set__(obj, value)
