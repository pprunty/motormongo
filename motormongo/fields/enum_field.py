import enum as pyenum

from motormongo.fields.field import Field


class EnumField(Field):
    def __init__(self, enum, **kwargs):
        super().__init__(type=pyenum.Enum, **kwargs)
        if not issubclass(enum, pyenum.Enum):
            raise TypeError("enum must be an enum.Enum subclass")
        self.enum = enum

    def __set__(self, obj, value):
        # If value is a string, try to match it with an enum member's value
        if isinstance(value, str):
            # Find a matching enum member, if any
            matching_enum = next(
                (
                    enum_member
                    for enum_member in self.enum
                    if enum_member.value == value
                ),
                None,
            )

            # If a match is found, set the enum member as the value
            if matching_enum is not None:
                value = matching_enum
            else:
                raise ValueError(
                    f"String value '{value}' does not match any member of {self.enum.__name__}"
                )

        # If value is not None and not an instance of the enum, raise an error
        if value is not None and not isinstance(value, self.enum):
            raise ValueError(
                f"Value for {self.name} must be an instance of {self.enum.__name__} or a matching string"
            )

        # Call the parent class's __set__ method
        super().__set__(obj, value)

    def __get__(self, obj, objtype=None):
        value = obj.__dict__.get(self.name, self.options.get("default"))
        # Return the enum member's value if the stored value is an enum member
        if isinstance(value, self.enum):
            return value.value
        return value
