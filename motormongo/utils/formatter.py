from datetime import datetime, timezone
from typing import re


def add_timestamps_if_required(cls, operation: str = "update", **kwargs):
    current_time = datetime.now(timezone.utc)
    if hasattr(cls, "Meta"):
        if (
            getattr(cls.Meta, "created_at_timestamp", False)
            and "created_at" not in kwargs
            and operation != "update"
        ):
            kwargs["created_at"] = current_time
        if (
            getattr(cls.Meta, "updated_at_timestamp", False)
            and "updated_at" not in kwargs
        ):
            kwargs["updated_at"] = current_time
    return kwargs


def camel_to_snake(name):
    """Convert CamelCase to snake_case."""
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()
