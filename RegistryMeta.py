class RegistryMeta(type):

    registry = {}

    def __init__(self, name, bases, attrs):
        super().__init__(name, bases, attrs)
        if name not in self.registry:
            RegistryMeta.registry[name] = self
        else:
            raise ValueError("cls have already in registery")
        
class ModelMeta(RegistryMeta):
    def __init__(cls, name, bases, attrs):
        super().__init__(name, bases, attrs)
        
        cls._fields = {}
        
        for attr_name, attr_value in attrs.items():
            if hasattr(attr_value, '__get__') or hasattr(attr_value, '__set__'):
                cls._fields[attr_name] = attr_value

class Model(metaclass=ModelMeta):
    pass

