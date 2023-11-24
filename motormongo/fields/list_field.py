from motormongo.fields.field import Field


class ListField(Field):
    def __init__(self, field=None, **kwargs):
        super().__init__(**kwargs)
        self.field = field  # Optional: a Field instance to validate list items

    def __set__(self, obj, value):
        if value is not None:
            if not isinstance(value, list):
                raise ValueError(f"Value for {self.name} must be a list")
            if self.field:
                # Validate each item in the list if a field type is provided
                for item in value:
                    if not isinstance(item, self.field.__class__):
                        raise ValueError(f"Items in {self.name} must be of type {self.field.__class__.__name__}")
        super().__set__(obj, value)
