class TypedProperty:

    def __init__(self, Type):
        self.__Type = Type
        self.name = None

    def __set_name__(self, owner, name):
        self.name = f"_{owner.__name__}__{name}"

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return instance.__dict__.get(self.name)
    
    def __set__(self, instance, value):
        if not isinstance(value, self.__Type):
            raise TypeError(f"incorrect type, need {self.__Type}")
        instance.__dict__[self.name] = value

class ValidatedProperty(TypedProperty):

    def __init__(self, Type, min_value = None, max_length = None):
        super().__init__(Type)
        self._min_value = min_value
        self._max_length = max_length
    
    def __set__(self, instance, value):
        super().__set__(instance, value)
        
        if self._min_value is not None and value < self._min_value:
            raise ValueError("not valid value")
        
        if self._max_length is not None and len(value) > self._max_length:
            raise ValueError("not valid length")
        
