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

class Entity:
    def free(self):
        self.__class__._free(self)

class Pool(type):
    __entities__ = set()
    __used__ = deque()
    def __new__(cls, name, bases, namespace):
        N = namespace.get("__pool_size__", 0)
        if N == 0:
            namespace["__pool_size__"] = N
        new_class = super().__new__(cls, name, bases + (Entity,), namespace)
        return new_class

    def _free(self, entity):
        print("free", entity)
        
    def __call__(self, *args, **kwargs):
        return super().__call__(*args, **kwargs)

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
    
    def __call__(self, *args, **kwargs):
        """Call the system to compute the entities.
        
        Example:
        
            .. code-block:: python
            
                class PhysicsSystem(toyblock3.System):
                    def _update(self, entity, dt):
                        entity.body.update(dt)
                        
                physics = PhysicsSystem()
                physics.add_entity(player)
                
                while not game_over:
                    physics(get_dt_time())
        
        """
        if self._locked: return
        entities = self._entities
        update = self._update
        self._locked = True
        for entity in entities:
            update(entity, *args, **kwargs)
        self._locked = False
        while self._remove_entity_list:
            self._entities.remove(self._remove_entity_list.pop())
        while self._add_entity_list:
            self._entities.append(self._add_entity_list.pop())

    def _update(self, entity, *args, **kwargs):
        raise NotImplementedError("Define an _update method for this system.")
