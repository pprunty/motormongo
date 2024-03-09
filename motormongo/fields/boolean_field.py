from motormongo.fields.exceptions import BooleanFieldError
from motormongo.fields.field import Field


class BooleanField(Field):
    def __init__(self, **kwargs):
        super().__init__(type=bool, **kwargs)

    def validate(self, value):
        """Validate the input value against the field's constraints."""
        if value is not None and not isinstance(value, bool):
            raise BooleanFieldError(
                f"Value for {self.name} must be a boolean. Got {type(value).__name__} of value: {value}."
            )
        return value

    def __set__(self, obj, value):
        validated_value = self.validate(
            value
        )  # Use validate method to process the value
        super().__set__(obj, validated_value)
