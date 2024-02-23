from motormongo.fields.exceptions import ListItemTypeError, ListValueTypeError
from motormongo.fields.field import Field


class ListField(Field):
    def __init__(self, field=None, **kwargs):
        super().__init__(type=list, **kwargs)
        self.field = field

    def __set__(self, obj, value):
        if value is not None:
            if not isinstance(value, list):
                raise ListValueTypeError(
                    f"Value for {self.name} must be a list. Got {type(value)} of value: {value}."
                )

            if self.field:
                for item in value:
                    if not isinstance(item, self.field.type):
                        raise ListItemTypeError(
                            f"Items in {self.name} must be of type {self.field.type}."
                        )

        super().__set__(obj, value)
