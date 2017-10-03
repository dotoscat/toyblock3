from collections import deque

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
            Entity._used.remove(entity)
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
    Entity._entities = deque(entities)
    Entity._used = deque()
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
        if not (isinstance(attrib, tuple) or isinstance(attrib, list)):
            raise ValueError("Pass a list or tuple with attribute names.")
        self._attrib = attrib
        self._callable_ = None
        self._entities = deque()
        self._locked = False
        self._add_entity_list = deque()
        self._remove_entity_list = deque()
    
    @property
    def callable(self):
        return self._callable_
        
    @callable.setter
    def callable(self, callable_):
        if self._callable_ is None:
            if not callable(callable_):
                raise ValueError("Use a callable object.")
            self._callable_ = callable_
    
    @property
    def attrib(self):
        return self._attrib
    
    @property
    def entities(self):
        return self._entities
    
    def _add_entity(self, entity):
        if self._locked:
            self._add_entity_list.append(entity)
        else:
            self._entities.append(entity)
    
    def _remove_entity(self, entity):
        if self._locked:
            self._remove_entity_list.append(entity)
        else:
            self._entities.remove(entity)
    
    def __call__(self, *args, **kwargs):
        if self._locked: return
        self._locked = True
        for entity in self._entities:
            self._callable_(self, entity, *args, **kwargs)
        self._locked = False
        while self._remove_entity_list:
            self._entities.remove(self._remove_entity_list.pop())
        while self._add_entity_list:
            self._entities.append(self._add_entity_list.pop())
        
def system(attributes):
    def _build_system(callable_):
        new_system = System(attributes)
        new_system.callable = callable_
        return new_system
    return _build_system
