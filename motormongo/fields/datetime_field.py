from datetime import date, datetime, timezone
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
        super().__init__(type=(datetime, date, str), **kwargs)
        self.auto_now = auto_now
        self.auto_now_add = auto_now_add

        # Set default formats if none provided
        default_formats = [
            "%Y-%m-%dT%H:%M:%S.%f",  # ISO 8601 with microseconds
            "%Y-%m-%dT%H:%M:%S",  # ISO 8601 without microseconds
            "%Y-%m-%d",  # ISO 8601 date only
            "%d/%m/%Y %H:%M:%S",  # Common British/European format with time
            "%m/%d/%Y %H:%M:%S",  # Common US format with time
            "%d/%m/%Y",  # Common British/European format without time
            "%m/%d/%Y",  # Common US format without time
            "%d-%b-%Y",  # Day-MonthName-Year e.g., 01-Jan-2020
            "%d-%b-%Y %H:%M:%S",  # Day-MonthName-Year with time
            "%B %d, %Y",  # FullMonthName Day, Year
            "%B %d, %Y %H:%M:%S",  # FullMonthName Day, Year with time
            "%Y%m%dT%H%M%S",  # Basic ISO-like without delimiters
            "%Y%m%d",  # Basic date without delimiters
        ]
        self.datetime_formats = (
            datetime_formats if datetime_formats is not None else default_formats
        )

    def validate(self, value):
        """Validate and convert the input value into a datetime object if necessary."""
        if isinstance(value, str):
            for fmt in self.datetime_formats:
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
            raise DateTimeFormatError(
                f"Value for {self.name} must be a datetime object, a date object, or a string in one of the formats: {', '.join(self.datetime_formats)}. Got {type(value)} of value: {value}."
            )
        elif isinstance(value, date) and not isinstance(value, datetime):
            return datetime(value.year, value.month, value.day)
        elif not isinstance(value, (datetime, date)):
            raise DateTimeValueError(
                f"Value for {self.name} must be a datetime object, a date object, or a string representation of datetime. Got {type(value).__name__} of value: {value}."
            )
        return value

    def __set__(self, obj, value):
        # If auto_now or auto_now_add flags are set, override the value with the current datetime
        if self.auto_now or (self.auto_now_add and not obj.__dict__.get(self.name)):
            value = datetime.now(timezone.utc)
        elif value is not None:
            value = self.validate(value)  # Validate and potentially convert the value
        super().__set__(obj, value)
