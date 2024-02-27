class Field:
    def __init__(self, type=None, required=False, unique=False, **kwargs):
        self.type = type if isinstance(type, tuple) else (type,)
        self.required = required
        self.unique = unique
        self.options = kwargs

    def __set_name__(self, owner, name):
        self.name = name
        owner._fields[name] = self  # Track fields in the owner (Document)

    def __get__(self, obj, objtype=None):
        return obj.__dict__.get(self.name, self.options.get("default"))

    def __set__(self, obj, value):
        if self.required and value is None:
            raise ValueError(f"The field '{self.name}' is required.")
        if not any(isinstance(value, t) for t in self.type if t is not None):
            allowed_types = ", ".join(t.__name__ for t in self.type if t is not None)
            raise TypeError(
                f"Value for {self.name} must be of type {allowed_types}. Got {type(value)} of value: {value}."
            )
        obj.__dict__[self.name] = value
