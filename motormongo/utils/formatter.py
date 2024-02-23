import re
from datetime import datetime, timezone


def add_timestamps_if_required(cls, operation: str = "update", **kwargs):
    now = datetime.now(timezone.utc)
    if hasattr(cls, "Meta"):
        if getattr(cls.Meta, "created_at_timestamp", True):
            if "created_at" not in kwargs and operation != "update":
                kwargs["created_at"] = now
        if getattr(cls.Meta, "updated_at_timestamp", True):
            kwargs["updated_at"] = now
    return kwargs


def camel_to_snake_or_lower(name: str) -> str:
    """Convert CamelCase to snake_case or string to lower.

    Args:
        name (str): The CamelCase name to convert.

    Returns:
        str: The converted snake_case name, or lowercase name.
    """
    # Check if the name is in CamelCase
    if not name or not re.match(r"^[A-Z][a-zA-Z0-9]+$", name):
        return name.lower()

    # Convert CamelCase to snake_case
    name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name).lower()
    return name


def enforce_types(args_with_types):
    """
    Enforces that the provided arguments match the expected types.

    Args:
        args_with_types (list of tuple): Each tuple in the list should contain:
            - The argument value
            - The expected type for the argument
            - A descriptive name for the argument (used in error messages)

    Raises:
        TypeError: If any of the arguments do not match their expected type.
    """
    for arg, expected_type, arg_name in args_with_types:
        if not isinstance(arg, expected_type):
            raise TypeError(
                f"Expected '{arg_name}' to be of type {expected_type.__name__}, got {type(arg).__name__} instead"
            )
