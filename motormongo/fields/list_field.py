from motormongo.fields.field import Field


class ListField(Field):
    def __init__(self, field=None, **kwargs):
        super().__init__(type=list, **kwargs)
        self.field = field

    def __set__(self, obj, value):
        if value is not None:
            if not isinstance(value, list):
                raise ValueError(f"Value for {self.name} must be a list")

            if self.field:
                for item in value:
                    if not isinstance(item, self.field.type):
                        raise ValueError(
                            f"Items in {self.name} must be of type {self.field.type.__name__}"
                        )

        super().__set__(obj, value)
