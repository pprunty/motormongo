class Field:
    def __init__(self, **kwargs):
        self.options = kwargs

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        return obj.__dict__.get(self.name, self.options.get('default'))

    def __set__(self, obj, value):
        obj.__dict__[self.name] = value

