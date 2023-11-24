from datetime import datetime

from motormongo.fields.field import Field


class DateTimeField(Field):
    def __init__(self, auto_now=False, auto_now_add=False, **kwargs):
        super().__init__(**kwargs)
        self.auto_now = auto_now
        self.auto_now_add = auto_now_add

    def __get__(self, obj, objtype=None):
        # If auto_now is set, return the current datetime
        if self.auto_now:
            return datetime.utcnow()
        return super().__get__(obj, objtype)

    def __set__(self, obj, value):
        if value is not None and not isinstance(value, datetime):
            raise ValueError(f"Value for {self.name} must be a datetime object")
        if self.auto_now_add and not obj.__dict__.get(self.name):
            value = datetime.utcnow()
        super().__set__(obj, value)
