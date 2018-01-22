#  Copyright (C) 2018 Oscar 'dotoscat' Triano

#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Lesser General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.

#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Lesser General Public License for more details.

#  You should have received a copy of the GNU Lesser General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

from collections import deque

class PoolableMixin:
    """Provide mechanisms to be used by :class:`Pool`.

    Don't use this class directly.
    """
    def __init__(self, pool, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__pool = pool
    def free(self):
        self.__pool.free(self)

def make_poolable(cls):
    """Make a class ready to be poolable.
    
    Returns:
        A :class:`Poolable`.

    Raises:
        NotImplementedError if :meth:`reset` is not implemented.
    """
    reset_method = getattr(cls, "reset", None)
    if not (callable(reset_method) and reset_method.__code__.co_argcount):
        raise NotImplementedError("Implement the reset method for {}".format(cls.__name__))
    poolable_class = type(cls.__name__, (PoolableMixin, cls), {})
    return poolable_class 

class Pool:
    """
    Create a pool of :class:`class_` n_entities.

    Any class passed by parameter it will be mixed with :class:`PoolableMixin`

    Parameters:
        class (type): Any class.
        n_entities (int): Number of entities for this pool
        *args: args for creating the instances.
        **kwargs: kwargs for creating the instances.

    Raises:
        NotImplementedError if the class has not implemented method:`reset`.

    Get an object from this pool just creating an instance. This instance
    has the *free* method.
    
    Example:
    
        .. code-block:: python
        
            class Body(Poolable):
                def __init__(self):
                    self.x = 0
                    self.y = 0
                    
                def reset(self):
                    self.x = 0
                    self.y = 0
        
            body_pool = Pool(Body, 10)

            one = body_pool()
            two = body_pool()
            one.free()
            two.free()
        
    """
    def __init__(self, class_, n_entities, *args, **kwargs):
        """Create a pool of :class:`class_` n_entities.

        Any class passed by parameter it will be mixed with :class:`PoolableMixin`

        Parameters:
            class (type): Any class.
            n_entities (int): Number of entities for this pool
            *args: args for creating the instances.
            **kwargs: kwargs for creating the instances.

        Raises:
            NotImplementedError if the class has not implemented method:`reset`.
        """
        reset_method = getattr(class_, "reset", None)
        if not (callable(reset_method) and reset_method.__code__.co_argcount):
            raise NotImplementedError("Implement the reset method for {}".format(class_.__name__))
        poolable_class = type(class_.__name__, (PoolableMixin, class_), {})
        self.entities = deque([poolable_class(self, *args, **kwargs) for i in range(n_entities)])
        self.used = deque()

    def free(self, entity):
        if entity not in self.used:
            return
        entity.reset()
        self.used.remove(entity)
        self.entities.append(entity)
        
    def __call__(self, *args, **kwargs):
        """Return an instance from its pool. None if there is not an avaliable entity."""
        if not self.entities:
            return None
        entity = self.entities.pop()
        self.used.append(entity)
        return entity

class System:
    def __init__(self):
        self._entities = deque()
        self._locked = False
        self._add_entity_list = deque()
        self._remove_entity_list = deque()
        
    @property
    def entities(self):
        """Return the current entities that are in this System."""
        return self._entities
    
    def add_entity(self, entity):
        if self._locked:
            self._add_entity_list.append(entity)
        else:
            self._entities.append(entity)
    
    def remove_entity(self, entity):
        if self._locked:
            self._remove_entity_list.append(entity)
        else:
            self._entities.remove(entity)
    
    def __call__(self):
        """Call the system to compute the entities.
        
        Example:
        
            .. code-block:: python
            
                class PhysicsSystem(toyblock3.System, dt):
                    def __init__(self):
                        super().__init__()
                        self.dt = dt

                    def _update(self, entity):
                        entity.body.update(self.dt)
                        
                physics = PhysicsSystem(STEP)
                physics.add_entity(player)
                
                while not game_over:
                    physics()
        
        """
        if self._locked: return
        entities = self._entities
        update = self._update
        self._locked = True
        for entity in entities:
            update(entity)
        self._locked = False
        while self._remove_entity_list:
            self._entities.remove(self._remove_entity_list.pop())
        while self._add_entity_list:
            self._entities.append(self._add_entity_list.pop())

    def _update(self, entity):
        raise NotImplementedError("Define an _update method for this system.")

class ManagedEntityMixin:
    def reset(self):
        super().reset()
        print("Systems", self.SYSTEMS)
        for system in self.SYSTEMS:
            pass
            # TODO: Remove entity from each system

class Manager:
    def __init__(self, poolable, n_entities, *args, **kwargs):
        managed_poolable = type(poolable.__name__, (ManagedEntityMixin, poolable), {})
        
