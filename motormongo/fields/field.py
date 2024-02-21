class Field:
    def __init__(self, type=None, **kwargs):
        # Allow for a single type or a tuple of types
        self.type = type if isinstance(type, tuple) else (type,)
        self.options = kwargs

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        return obj.__dict__.get(self.name, self.options.get("default"))

    def __set__(self, obj, value):
        # Check against all allowed types
        if not any(isinstance(value, t) for t in self.type if t is not None):
            allowed_types = ", ".join(t.__name__ for t in self.type if t is not None)
            raise TypeError(
                f"Value for {self.name} must be of type {allowed_types}. Got {type(value)}."
            )
        obj.__dict__[self.name] = value
