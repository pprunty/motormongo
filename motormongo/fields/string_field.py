from motormongo.fields.field import Field


class StringField(Field):
    def __init__(self, min_length=None, max_length=None, regex=None, **kwargs):
        super().__init__(**kwargs)
        self.min_length = min_length
        self.max_length = max_length
        self.regex = regex

    def __set__(self, obj, value):
        if value is not None:
            if not isinstance(value, str):
                raise ValueError(f"Value for {self.name} must be a string: {value} is of type {type(value)}")
            if self.min_length is not None and len(value) < self.min_length:
                raise ValueError(f"Value for {self.name} must be at least {self.min_length} characters: '{value}'")
            if self.max_length is not None and len(value) > self.max_length:
                raise ValueError(f"Value for {self.name} must be no more than {self.max_length} characters: '{value}'")
            if self.regex and not self.regex.match(value):
                raise ValueError(f"Value for {self.name} does not match required regex pattern ({self.regex}): '{value}'")
        super().__set__(obj, value)
