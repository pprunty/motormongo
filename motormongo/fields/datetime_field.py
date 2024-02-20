from datetime import date, datetime
from typing import List

from motormongo.fields.exceptions import DateTimeFormatError, DateTimeValueError
from motormongo.fields.field import Field


class DateTimeField(Field):
    def __init__(
        self,
        auto_now: bool = False,
        auto_now_add: bool = False,
        datetime_formats: List[str] = None,
        **kwargs,
    ):
        super().__init__(type=(datetime, date, str, None), **kwargs)
        self.auto_now = auto_now
        self.auto_now_add = auto_now_add
        if datetime_formats is None:
            datetime_formats = ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"]
        self.datetime_formats = (
            [datetime_formats]
            if isinstance(datetime_formats, str)
            else datetime_formats
        )

    def __set__(self, obj, value):
        if value is not None:
            if isinstance(value, str):
                parsed = False
                for fmt in self.datetime_formats:
                    try:
                        value = datetime.strptime(value, fmt)
                        parsed = True
                        break
                    except ValueError:
                        continue
                if not parsed:
                    raise DateTimeFormatError(
                        f"Value for {self.name} must be a datetime object, a date object, or a string in one of the formats: {', '.join(self.datetime_formats)}. Got {type(value)}."
                    )
            elif isinstance(value, date) and not isinstance(value, datetime):
                value = datetime(value.year, value.month, value.day)
            elif not isinstance(value, (datetime, date)):
                raise DateTimeValueError(
                    f"Value for {self.name} must be a datetime object, a date object, or a string representation of datetime. Got {type(value)}."
                )

        if self.auto_now or (self.auto_now_add and not obj.__dict__.get(self.name)):
            value = datetime.utcnow()

        super().__set__(obj, value)
