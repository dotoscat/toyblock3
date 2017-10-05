import unittest
import toyblock3

class TestSystem(unittest.TestCase):
        
    def test1_system_creation(self):
        @toyblock3.system("a", "b", "c")
        def get_true(system, entity, test):
            print(system, entity, test)
            test.assertTrue(True)
        get_true(self)
        self.assertTrue(get_true.components == ("a", "b", "c"))
        
    def test2_wrong_attributes_list(self):
        with self.assertRaises(ValueError):
            @toyblock3.system({})
            def one(): pass
            @toyblock3.system(7)
            def two(): pass
            
    def test_wrong_callable(self):
        with self.assertRaises(ValueError):
            build_system = toyblock3.system(('a',))
            build_system(1)

class TestEntity(unittest.TestCase):
    
    def setUp(self):
        @toyblock3.system("a", "b")
        def a_system(system, entity, n):
            print(system, entity, n)
            
        self.a_system = a_system
    
    def test1_entity_creation(self):
        attributes = ("a",)
        
        @toyblock3.system("c")
        def c_system(system, entity):
            print(system, entity)
        
        A = toyblock3.factory(attributes, (self.a_system, c_system), 10)
        self.assertTrue(len(A._entities) == 10)
        self.assertTrue(isinstance(A._entities[0], A))
        a = A.get()
        a.free()
        b = A.get()
        self.assertTrue(a is b)
        self.assertTrue(self.a_system in A._systems)
        self.assertTrue(c_system._entities not in A._systems)
        self.a_system(7)
        c_system()
