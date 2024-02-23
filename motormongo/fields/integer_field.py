from motormongo.fields.exceptions import IntegerRangeError, IntegerValueError
from motormongo.fields.field import Field


class IntegerField(Field):
    def __init__(self, min_value=None, max_value=None, **kwargs):
        super().__init__(type=int, **kwargs)
        self.min_value = min_value
        self.max_value = max_value

    def __set__(self, obj, value):
        if value is not None:
            if not isinstance(value, int):
                raise IntegerValueError(
                    f"Value for {self.name} must be an integer. Got {type(value)} of value: {value}."
                )
            if self.min_value is not None and value < self.min_value:
                raise IntegerRangeError(
                    f"Value for {self.name} must be at least {self.min_value}"
                )
            if self.max_value is not None and value > self.max_value:
                raise IntegerRangeError(
                    f"Value for {self.name} must be no more than {self.max_value}"
                )
        super().__set__(obj, value)
