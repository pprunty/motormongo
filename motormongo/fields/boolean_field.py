from motormongo.fields.exceptions import BooleanFieldError
from motormongo.fields.field import Field


class BooleanField(Field):
    def __init__(self, **kwargs):
        super().__init__(type=bool, **kwargs)

    def __set__(self, obj, value):
        if value is not None and not isinstance(value, bool):
            raise BooleanFieldError(
                f"Value for {self.name} must be a boolean. Got {type(value)} of value: {value}."
            )
        super().__set__(obj, value)
