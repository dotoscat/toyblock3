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
        class Rectangle:
            def __init__(self, a, b):
                self.a = a
                self.b = b
            def reset(self):
                pass

        class RectangleWoReset:
           pass

        RectanglePool = toyblock3.Pool(Rectangle, 8, 7, 12)
        other_rect = self.assertRaises(NotImplementedError, toyblock3.Pool, RectangleWoReset, 4)
        self.assertEqual(len(RectanglePool.entities), 8, "There are not 8 rectangles")
        rect = RectanglePool()
        self.assertEqual(rect.a, 7, "Rect a is not equal to 7")
        self.assertEqual(rect.b, 12, "Rect a is not equal to 12")
        rect.reset()
        rect.free()
        rect.free()
        self.assertEqual(len(RectanglePool.entities), 8, "There are not 8 rectangles")