def factory(attributes, systems, n):
    class Entity:
        
        @classmethod
        def get(Entity):
            entity = None
            if Entity._entities:
                entity = Entity._entities.pop()
                Entity._used.append(entity)
            return entity
        
        @classmethod
        def _free(Entity, entity):
            index = Entity._used.index(entity)
            Entity._used.pop(index)
            Entity._entities.append(entity)
        
        def free(self):
            self.__class__._free(self)
        
    Entity._entities = [Entity() for i in range(n)]
    Entity._used = []
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
