from collections import deque

def _check_components_are(components, type_):
    if not (isinstance(components, tuple) or isinstance(components, list)):
        raise ValueError("Pass a tuple or list with {}.").format(type_)
    for component in components:
        if not isinstance(component, type_):
            raise ValueError("Pass {} as parameters. Found a {}".format(type_, type(component)))

class EntityBuilder:
    def __init__(self):
        self._component = {}
        self._iterator = None
        
    def add(self, component, type_, *args, **kwargs):
        # Check types or arguments
        self._component[component] = {"type": type_, "args": args, "kwargs": kwargs}
        return self

    def __iter__(self):
        self._iterator = iter(self._component)
        return self
        
    def __next__(self):
        key = next(self._iterator)
        type_ = self._component[key]["type"]
        args = self._component[key]["args"]
        kwargs = self._component[key]["kwargs"]
        return key, type_(*args, **kwargs)
    
def factory(components, systems, n):

    _check_components_are(components, str)
    _check_components_are(systems, System)
    if not isinstance(n, int):
        raise ValueError("Pass an intenger. Found {}".format(type(n)))

    class Entity:
        __slots__ = components
        
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
                
        @classmethod
        def attrib(Entity):
            return Entity._attrib
        
        def free(self):
            self.__class__._free(self)
    
    entities = [Entity() for i in range(n)]
    
    Entity._components = components
    Entity._entities = deque(entities)
    Entity._used = deque()
    Entity._systems = []
    
    for system in systems:
        insert = False
        for component in components:
            insert = insert or component in system.components
            if not insert: continue
            Entity._systems.append(system)
    
    return Entity

class System:
    def __init__(self, *components):
        _check_components_are(components, str)
        self._components = components
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
    def components(self):
        return self._components
    
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
        entities = self._entities
        callable_ = self._callable_
        self._locked = True
        for entity in entities:
            callable_(self, entity, *args, **kwargs)
        self._locked = False
        while self._remove_entity_list:
            self._entities.remove(self._remove_entity_list.pop())
        while self._add_entity_list:
            self._entities.append(self._add_entity_list.pop())
        
def system(*components):
    def _build_system(callable_):
        new_system = System(*components)
        new_system.callable = callable_
        return new_system
    return _build_system
