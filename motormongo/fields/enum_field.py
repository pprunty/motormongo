import enum as pyenum

from motormongo.fields.exceptions import InvalidEnumTypeError, InvalidEnumValueError
from motormongo.fields.field import Field


class EnumField(Field):
    def __init__(self, enum, **kwargs):
        super().__init__(type=pyenum.Enum, **kwargs)
        if not issubclass(enum, pyenum.Enum):
            raise InvalidEnumTypeError("enum must be an enum.Enum subclass")
        self.enum = enum

    def validate(self, value):
        """Validate or convert the value to the corresponding enum member."""
        if isinstance(value, str):
            # Attempt to find a matching enum member by string value
            matching_enum = next(
                (
                    enum_member
                    for enum_member in self.enum
                    if enum_member.value == value
                ),
                None,
            )
            if matching_enum is not None:
                return matching_enum
            else:
                raise InvalidEnumValueError(
                    f"String value '{value}' does not match any member of {self.enum.__name__}"
                )
        elif value is not None and not isinstance(value, self.enum):
            raise InvalidEnumTypeError(
                f"Value for {self.name} must be an instance of {self.enum.__name__} or a matching string. Got {type(value).__name__} of value: {value}."
            )
        return value

    def __set__(self, obj, value):
        if value is not None:
            validated_value = self.validate(
                value
            )  # Use validate method to process the value
            super().__set__(obj, validated_value)
        else:
            super().__set__(obj, value)

    def __get__(self, obj, objtype=None):
        # Get the enum member and return its value
        value = obj.__dict__.get(self.name, self.options.get("default"))
        if isinstance(value, self.enum):
            return value.value
