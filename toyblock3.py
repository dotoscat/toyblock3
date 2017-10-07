from collections import deque

def _check_components_are(components, type_):
    if not (isinstance(components, tuple) or isinstance(components, list)):
        raise ValueError("Pass a tuple or list with {}.").format(type_)
    for component in components:
        if not isinstance(component, type_):
            raise ValueError("Pass {} as parameters. Found a {}".format(type_, type(component)))

class InstanceBuilder:
    """Define what are the components.
    
    This is a helper class to :func:`build_Entity` (and for you)
    
    Example:
        
        .. code-block:: python
        
            builder = toyblock3.InstanceBuilder()
            builder.add("body", Body, x=32, y=32)
            
    """
    def __init__(self):
        self._components = {}
        self._iterator = None
        
    def add(self, component, type_, *args, **kwargs):
        """Defines what a component is.
        
        Add a component with its type and arguments.
        
        It is possible chain :meth:`InstanceBuilder.add`.
        
        Returns:
            This instance
        
        Raises:
            ValueError if :obj:`component` is not a :class:`str`.
        """
        if not isinstance(component, str):
            raise ValueError("component must be a String type. {} given.".format(type(component)))
        self._components[component] = {"type": type_, "args": args, "kwargs": kwargs}
        return self

    @property
    def components(self):
        """Return a tuple with the components added to this builder until now."""
        return tuple(self._components.keys())
        
    def __iter__(self):
        self._iterator = iter(self._components)
        return self
        
    def __next__(self):
        component = next(self._iterator)
        type_ = self._components[component]["type"]
        args = self._components[component]["args"]
        kwargs = self._components[component]["kwargs"]
        return component, type_(*args, **kwargs)

def build_Entity(n, instance_builder, *systems):
    _check_components_are(systems, System)
    if not isinstance(n, int):
        raise ValueError("Pass an intenger. Found {}".format(type(n)))
    if not isinstance(instance_builder, InstanceBuilder):
        raise ValueError("Pass an InstanceBuilder. Found {}".format(type(n)))

    class Entity:
        __slots__ = instance_builder.components
        
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
        def components(Entity):
            return Entity._components
        
        def free(self):
            self.__class__._free(self)
    
    entities = deque((Entity() for i in range(n)))
    for entity in entities:
        for component, instance in instance_builder:
            setattr(entity, component, instance)
    
    Entity._components = instance_builder.components
    Entity._entities = entities
    Entity._used = deque()
    Entity._systems = []
    
    for system in systems:
        insert = False
        for component in instance_builder.components:
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
        """You can only set this property once.
        
        This property is visible if you write a class that inherits
        from :class:`System`.
        
        :func:`system` decorator will set the callable for you.
        
        Raises:
            ValueError if the object assigned is not a *callable*.
        """
        return self._callable_
        
    @callable.setter
    def callable(self, callable_):
        if self._callable_ is None:
            if not callable(callable_):
                raise ValueError("Use a callable object.")
            self._callable_ = callable_
    
    @property
    def components(self):
        """Components defined for this System."""
        return self._components
    
    @property
    def entities(self):
        """Return the current entities that are in this System."""
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
        """Call the system to compute the entities.
        
        Example:
        
            .. code-block:: python
            
                @toyblock3.system('body')
                def physics(system, entity, dt):
                    entity.body.update(dt)
                    for other_entity in system.entities:
                        check_collision_with(entity, other_entity)
                        #  more stuff
                    
                #  Add some entities to this system.
                
                while not game_over:
                    physics(get_dt_time())
        
        """
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
    """Convenient decorator with arguments to build a System instance.
    
    Arguments:
        *components (:class:`str`): Member names of an :class:`Entity`
    
    Raises:
        ValueError if any component is not a :class:`str`
    
    Returns:
        An instance of :class:`System`
    
    Example:
    
        .. code-block:: python
        
            @toyblock3.system('body', 'sprite')
            def update_sprite(system, entity):
                entity.sprite.set(body.position)
    
    """
    def _build_system(callable_):
        new_system = System(*components)
        new_system.callable = callable_
        return new_system
    return _build_system
