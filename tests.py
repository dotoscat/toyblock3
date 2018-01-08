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
            def _update(self, entity):
                print("Hola mundo")
                
        system = MySystem()
        system.add_entity(A())
        system()
        
class TestPool(unittest.TestCase):
    
    def test1_pool_creation(self):
        
        class B(metaclass=toyblock3.Pool):
            POOL_SIZE = 3
            pass
        
        class C(metaclass=toyblock3.Pool):
            POOL_SIZE = 7
            pass
        
        print("class B", B)
        
        b = B()
        c = C()
        b.free()
        
        print(B.POOL_SIZE, C.POOL_SIZE)
        
