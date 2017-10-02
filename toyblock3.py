def factory(attributes, systems, n):
    class Entity:
        
        @classmethod
        def get(Entity):
            entity = None
            if Entity._entities:
                entity = Entity._entities.pop()
                Entity._used.append(entity)
                for system in Entity._systems:
                    system._add_entity(entity)
            return entity
        
        @classmethod
        def _free(Entity, entity):
            index = Entity._used.index(entity)
            Entity._used.pop(index)
            Entity._entities.append(entity)
            for system in Entity._systems:
                system._remove_entity(entity)
        
        @property
        def attrib(self):
            self.__class__._attrib
        
        def free(self):
            self.__class__._free(self)
    
    entities = [Entity() for i in range(n)]
    
    Entity._attrib = attributes #  Replace later by __slots__
    Entity._entities = entities
    Entity._used = []
    Entity._systems = []
    
    for system in systems:
        insert = False
        for attr in attributes:
            insert = insert or attr in system.attrib
            if not insert: continue
            Entity._systems.append(system)
    
    return Entity

class System:
    def __init__(self, attrib):
        self._attrib = attrib
        self._callable_ = None
        self._entities = []
        self._locked = False
    
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
    
    @property
    def entities(self):
        return self._entities
    
    def _add_entity(self, entity):
        self._entities.append(entity)
    
    def _remove_entity(self, entity):
        index = self._entities.index(entity)
        self._entities.pop(index)
    
    def __call__(self, *args, **kwargs):
        if self._locked: return
        self._locked = True
        for entity in self._entities:
            self._callable_(self, entity, *args, **kwargs)
        self._locked = False
        
def system(attributes):
    def _build_system(callable_):
        new_system = System(attributes)
        new_system.callable = callable_
        return new_system
    return _build_system
