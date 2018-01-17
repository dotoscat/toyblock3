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

    def test1_poolable(self):
        @toyblock3.make_poolable
        class Rectangle:
            def __init__(self, a, b):
                self.a = a
                self.b = b

        self.assertTrue(issubclass(Rectangle, toyblock3.Poolable))

        RectanglePool = toyblock3.Pool(Rectangle, 8, 0, 0)
        self.assertEqual(len(RectanglePool.entities), 8, "There are not 8 rectangles")
        