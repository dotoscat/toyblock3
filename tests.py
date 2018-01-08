import unittest
import toyblock3

class A:
    pass

class TestSystem(unittest.TestCase):
        
    def test1_abtract_class_not_implemented(self):
        system = toyblock3.System()
        system.add_entity(A())
        self.assertRaises(NotImplementedError, system)

    def test2_implemented(self):
        
        class MySystem(toyblock3.System):
            def _update(self, entity, *args, **kwargs):
                print("Hola mundo")
                
        system = MySystem()
        system.add_entity(A())
        system()
        
