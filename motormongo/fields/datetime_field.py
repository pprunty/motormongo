from datetime import datetime, date

from motormongo.fields.field import Field


class DateTimeField(Field):
    def __init__(self, auto_now=False, auto_now_add=False, datetime_formats=None, **kwargs):
        super().__init__(type=(datetime, date, str, None), **kwargs)
        self.auto_now = auto_now
        self.auto_now_add = auto_now_add
        # Set default formats if none provided
        if datetime_formats is None:
            datetime_formats = ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]
        self.datetime_formats = datetime_formats

    def __set_name__(self, owner, name):
        super().__set_name__(owner, name)

    def __get__(self, obj, objtype=None):
        if self.auto_now:
            return datetime.utcnow()
        return super().__get__(obj, objtype)

    def __set__(self, obj, value):
        if value is not None:
            if isinstance(value, str):
                parsed = False
                for fmt in self.datetime_formats:
                    try:
                        parsed_value = datetime.strptime(value, fmt)
                        value = parsed_value
                        parsed = True
                        break  # Parsing succeeded
                    except ValueError:
                        continue  # Try the next format
                if not parsed:
                    formats_str = ", ".join(self.datetime_formats)
                    raise ValueError(f"Value for {self.name} must be a datetime object, a date object, or a string in one of the formats: {formats_str}")
            elif isinstance(value, date) and not isinstance(value, datetime):
                # Convert date to datetime for consistency
                value = datetime(value.year, value.month, value.day)
            elif not isinstance(value, datetime):
                raise ValueError(f"Value for {self.name} must be a datetime object, a date object, or a string representation of datetime")

        if self.auto_now or (self.auto_now_add and not obj.__dict__.get(self.name)):
            value = datetime.utcnow()

        super().__set__(obj, value)
