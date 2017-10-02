def factory(attributes, systems, n):
    class Entity:
        pass
    entities = [Entity() for i in range(n)]
    Entity.entities = entities
    return Entity

class System:
    def __init__(self, attrib):
        self._attrib = attrib
        self._callable_ = None
    
    @property
    def callable(self):
        return self._callable_
        
    @callable.setter
    def callable(self, callable_):
        if self._callable_ is None:
            self._callable_ = callable_
    
    @property
    def attrib(self):
        return self._attrib
    
    def __call__(self, *args, **kwargs):
        return self._callable_(*args, **kwargs)

def system(attributes):
    def _build_system(callable_):
        new_system = System(attributes)
        new_system.callable = callable_
        return new_system
    return _build_system
