class Field:
    def __init__(self, type=None, **kwargs):
        self.type = type
        self.options = kwargs

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        return obj.__dict__.get(self.name, self.options.get('default'))

    def __set__(self, obj, value):
        if self.type and not isinstance(value, self.type):
            raise TypeError(f"Value for {self.name} must be of type {self.type.__name__}")
        obj.__dict__[self.name] = value
