from datetime import date, datetime, timezone
from typing import Iterable, List

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
        super().__init__(type=(datetime, date, str), **kwargs)
        self.auto_now = auto_now
        self.auto_now_add = auto_now_add

        # Set default formats if none provided
        default_formats = ["%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]

        # Ensure datetime_formats is a list
        if datetime_formats is None:
            self.datetime_formats = default_formats
        elif isinstance(datetime_formats, str):
            self.datetime_formats = [datetime_formats]
        elif isinstance(
            datetime_formats, Iterable
        ):  # Check if it's an iterable (list, tuple, etc.)
            self.datetime_formats = list(datetime_formats)
        else:
            raise ValueError(
                "datetime_formats must be a string or an iterable of strings."
            )

    def _handle_string_or_date_input(self, value):
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
                    f"Value for {self.name} must be a datetime object, a date object, or a string in one of the formats: {', '.join(self.datetime_formats)}. Got {type(value)} of value: {value}."
                )
        elif isinstance(value, date) and not isinstance(value, datetime):
            value = datetime(value.year, value.month, value.day)
        elif not isinstance(value, (datetime, date)):
            raise DateTimeValueError(
                f"Value for {self.name} must be a datetime object, a date object, or a string representation of datetime. Got {type(value)} of value: {value}."
            )
        return value

    def __set__(self, obj, value):
        # If auto_now_add and field is empty, set value = now
        if self.auto_now_add and not obj.__dict__.get(self.name):
            value = datetime.now(timezone.utc)
            super().__set__(obj, value)
            return
        # Else, if auto_now_add and field is non-empty, set value = value
        elif self.auto_now_add and obj.__dict__.get(self.name):
            value = obj.__dict__.get(self.name)
            super().__set__(obj, value)
            return
        else:
            # Handle string or date inputs (as before)
            if value is not None:
                value = self._handle_string_or_date_input(value)

        super().__set__(obj, value)
