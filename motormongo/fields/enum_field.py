import enum as pyenum

from motormongo.fields.exceptions import InvalidEnumTypeError, InvalidEnumValueError
from motormongo.fields.field import Field


class EnumField(Field):
    def __init__(self, enum, **kwargs):
        super().__init__(type=pyenum.Enum, **kwargs)
        if not issubclass(enum, pyenum.Enum):
            raise InvalidEnumTypeError("enum must be an enum.Enum subclass")
        self.enum = enum

    def __set__(self, obj, value):
        if isinstance(value, str):
            matching_enum = next(
                (
                    enum_member
                    for enum_member in self.enum
                    if enum_member.value == value
                ),
                None,
            )
            if matching_enum is not None:
                value = matching_enum
            else:
                raise InvalidEnumValueError(
                    f"String value '{value}' does not match any member of {self.enum.__name__}"
                )
        elif value is not None and not isinstance(value, self.enum):
            raise InvalidEnumTypeError(
                f"Value for {self.name} must be an instance of {self.enum.__name__} or a matching string. Got {type(value)} of value: {value}."
            )

        super().__set__(obj, value)

    def __get__(self, obj, objtype=None):
        value = obj.__dict__.get(self.name, self.options.get("default"))
        if isinstance(value, self.enum):
            return value.value
        return value
