import enum

from motormongo.fields.field import Field


class EnumField(Field):
    def __init__(self, enum_type, **kwargs):
        super().__init__(**kwargs)
        if not issubclass(enum_type, enum.Enum):
            raise TypeError("enum_type must be an enum.Enum subclass")
        self.enum_type = enum_type

    def __set__(self, obj, value):
        if value is not None and not isinstance(value, self.enum_type):
            raise ValueError(f"Value for {self.name} must be an instance of {self.enum_type.__name__}")
        super().__set__(obj, value)

    def __get__(self, obj, objtype=None):
        value = obj.__dict__.get(self.name, self.options.get('default'))
        if isinstance(value, self.enum_type):
            return value.value
        return value
