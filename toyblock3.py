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
    def __init__(self):
        self.systems = set()

    def add_system(self, system):
        pass
        
    def remove_system(self, system):
        pass

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
