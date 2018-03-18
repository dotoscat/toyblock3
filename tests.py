import unittest
import toyblock3

class A:
    pass
    def reset(self):
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
        self.assertEqual(len(RectanglePool.used), 1, "rect is not used!")
        self.assertEqual(rect.a, 7, "Rect a is not equal to 7")
        self.assertEqual(rect.b, 12, "Rect a is not equal to 12")
        rect.reset()
        rect.free()
        rect.free()
        self.assertEqual(len(RectanglePool.used), 0, "rect is not freed!")
        self.assertEqual(len(RectanglePool.entities), 8, "There are not 8 rectangles")

    def test2_free_all(self):
        a_pool = toyblock3.Pool(A, 10)
        for i in range(7):
            a_pool()
        self.assertEqual(len(a_pool.used), 7, "No 7 entities used")
        a_pool.free_all()
        self.assertEqual(len(a_pool.used), 0, "No all entities freed")

class ManagerTest(unittest.TestCase):
    def test1_manager(self):

        class IncrementSystem(toyblock3.System):
            def _update(self, entity):
                entity.value += 1

        increment_system = IncrementSystem()

        class PrintSystem(toyblock3.System):
            def _update(self, entity):
                print(entity, entity.value)

        print_system = PrintSystem()

        class Box:
            DEFAULT_VALUE = 0
            SYSTEMS = (increment_system, print_system)
            def __init__(self, value=0):
                self.value = value
            def reset(self):
                self.value = self.DEFAULT_VALUE
                print("reset value", self.value)

        box_manager = toyblock3.Manager(Box, 4, 7)
        a_box = box_manager()
        increment_system()
        print_system()
        a_box.free() 
        increment_system()
        print_system()