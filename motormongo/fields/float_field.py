from motormongo.fields.field import Field


class FloatField(Field):
    def __init__(self, min_value=None, max_value=None, **kwargs):
        super().__init__(type=float, **kwargs)
        self.min_value = min_value
        self.max_value = max_value

    def __set__(self, obj, value):
        # Validate that the value is a float
        if value is not None:
            if not isinstance(value, (float, int)):  # Accept integers as they can be cast to float
                raise ValueError(f"Value for {self.name} must be a float or int")

            # Convert integers to float for consistent storage
            value = float(value)

            # Check for minimum value
            if self.min_value is not None and value < self.min_value:
                raise ValueError(f"Value for {self.name} must be at least {self.min_value}")

            # Check for maximum value
            if self.max_value is not None and value > self.max_value:
                raise ValueError(f"Value for {self.name} must be no more than {self.max_value}")

        super().__set__(obj, value)

    def __get__(self, obj, objtype=None):
        return obj.__dict__.get(self.name, self.options.get('default'))
