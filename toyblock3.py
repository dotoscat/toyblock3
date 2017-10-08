from collections import deque

def _check_components_are(components, type_):
    if not (isinstance(components, tuple) or isinstance(components, list)):
        raise ValueError("Pass a tuple or list with {}.").format(type_)
    for component in components:
        if not isinstance(component, type_):
            raise ValueError("Pass {} as parameters. Found a {}".format(type_, type(component)))

class InstanceBuilder:
    """Define what are the components.
    
    This is a helper class for :func:`build_Entity` (and for you).
    
    Example:
        
        .. code-block:: python
        
            builder = toyblock3.InstanceBuilder()
            builder.add("body", Body, x=32, y=32)
            builder.add("sprite", Sprite, hero_image)
    """
    def __init__(self):
        self._components = {}
        self._iterator = None
        
    def add(self, component, type_, *args, **kwargs):
        """Defines what a component is.
        
        Add a component with its type and arguments.
        
        It is possible chain :meth:`InstanceBuilder.add`.
        
        Returns:
            This instance.
        
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

class Entity:
    __slots__ = ()
    """Pool of :class:`Entity` instances.
    
    You can access to any instance defined for this Entity.
    Each Entity are different from each other but they have the same interface.
    
    This class is not meant to be used directly. See :func:`build_Entity`.
    
    Example:
    
        .. code-block:: python
        
            toyblock3.system('body')
            def out_of_bounds(system, entity, bounds):
                if not in bounds:
                    entity.free()
            
            Bullet = toyblock3.build_Entity(100, builder, out_of_bounds, physics, update_sprite)
            
            def shoot(Bullet, x, y):
                a_bullet = Bullet.get()
                a_bullet.body.x = x
                a_bullet.body.y = y
    """
        
    @classmethod
    def get(cls):
        """Return an unused instance from its pool."""
        entity = None
        if cls._entities:
            entity = cls._entities.pop()
            cls._used.append(entity)
            for system in cls._systems:
                system._add_entity(entity)
        return entity
    
    @classmethod
    def _free(cls, entity):
        cls._used.remove(entity)
        cls._entities.append(entity)
        for system in cls._systems:
            system._remove_entity(entity)
            
    @classmethod
    def components(cls):
        """Get a tuple of the components defined for this :class:`Entity`."""
        return cls._components
    
    def free(self):
        """Free this entity.
        
        Raises:
            NotImplementedError if :class:`Entity` is being used directly.
        """
        raise NotImplementedError("Do not use Entity directly. Use build_Entity.")
        
def build_Entity(n, instance_builder, *systems):
    """Create an custom :class:`Entity`.
    
    Create a pool of n instances from a custom :class:`Entity` builded from
    the instance_builder and the systems added.
    
    If there is a component that is not found in a system, that entity will not added to that System.
    
    Parameters:
        n (int): Number of entities created for :class:`Entity`.
        instance_builder(InstanceBuilder):
        systems (System):
    
    Returns:
        A custom :class:`Entity`.
    
    Raises:
        ValueError: :obj:`n` is not a :class:`int`
        ValueError: :obj:`instance_builder` is not a :class:`InstanceBuilder`.
    
    Example:
        
        .. code-block:: python
        
            @toyblock3.system('body')
            def physics(system, entity, dt):
                #  add stuff
    
            @toyblock3.system('body', 'sprite')
            def update_sprite(system, entity):
                #  more stuff
    
            builder = toyblock3.InstanceBuilder()
            builder.add("body", Body, x=x, y=y)
            builder.add("sprite", Sprite, bullet_image)
            
            Bullet = toyblock3.build_Entity(100, builder, physics, update_sprite)
    """
    _check_components_are(systems, System)
    if not isinstance(n, int):
        raise ValueError("Pass an intenger. Found {}".format(type(n)))
    if not isinstance(instance_builder, InstanceBuilder):
        raise ValueError("Pass an InstanceBuilder. Found {}".format(type(instance_builder)))

    class _EntityMeta(type):
        def __new__(cls, name, bases, dctn):
            dctn["__slots__"] = instance_builder.components
            return type.__new__(cls, name, (Entity,), dctn)
    
    class _Entity(metaclass=_EntityMeta):

        def free(self):
            self.__class__._free(self)
    
    entities = deque((_Entity() for i in range(n)))
    for entity in entities:
        for component, instance in instance_builder:
            setattr(entity, component, instance)
    
    _Entity._components = instance_builder.components
    _Entity._entities = entities
    _Entity._used = deque()
    _Entity._systems = []
    
    for system in systems:
        insert = False
        for component in instance_builder.components:
            insert = insert or component in system.components
            if not insert: continue
            _Entity._systems.append(system)
    
    return _Entity

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
                entity.sprite.set(entity.body.position)
    
    """
    def _build_system(callable_):
        new_system = System(*components)
        new_system.callable = callable_
        return new_system
    return _build_system
