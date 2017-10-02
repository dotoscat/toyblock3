import unittest
import toyblock3

class TestSystem(unittest.TestCase):
        
    def test1_system_creation(self):
        @toyblock3.system(("a", "b", 7))
        def get_true(value):
            return value
            
        self.assertTrue(get_true(True))
        self.assertTrue(get_true.attrib == ("a", "b", 7))

class TestEntity(unittest.TestCase):
    
    def setUp(self):
        @toyblock3.system(("a", "b"))
        def a_system(system, entity):
            print(system, entity)
            
        self.a_system = a_system
    
    def test1_entity_creation(self):
        attributes = ("a",)
        
        A = toyblock3.factory(attributes, (self.a_system,), 10)
        self.assertTrue(len(A._entities) == 10)
        self.assertTrue(isinstance(A._entities[0], A))
        a = A.get()
        a.free()
        b = A.get()
        self.assertTrue(a is b)
        self.assertTrue(len(self.a_system._entities) == 10)
