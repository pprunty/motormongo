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

    def _parse_string_to_datetime(self, value):
        for fmt in self.datetime_formats:
            try:
                return datetime.strptime(value, fmt), True
            except ValueError:
                continue
        return value, False

    def _convert_to_datetime(self, value):
        if isinstance(value, str):
            value, parsed = self._parse_string_to_datetime(value)
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
        if self.auto_now_add:
            existing_value = obj.__dict__.get(self.name)
            value = (
                existing_value or datetime.now(timezone.utc)
                if not existing_value
                else value
            )
        elif self.auto_now:
            value = datetime.now(timezone.utc)

        if value is not None:
            value = self._convert_to_datetime(value)

        super().__set__(obj, value)
