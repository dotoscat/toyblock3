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
        with self.assertRaises(TypeError):
            @toyblock3.system({})
            def one(): pass
            @toyblock3.system(7)
            def two(): pass
            
    def test_wrong_callable(self):
        with self.assertRaises(TypeError):
            build_system = toyblock3.system(('a',))
            build_system(1)

class TestEntity(unittest.TestCase):
    
    def setUp(self):
        @toyblock3.system("a", "b")
        def a_system(system, entity, n):
            print(system, entity, n)
            
        self.a_system = a_system
        
        class A:
            def __init__(self, x=0., y=0.):
                self.x = x
                self.y = y
        
        builder = toyblock3.InstanceBuilder()
        builder.add("pair", dict, x=32, y=32)
        builder.add("id", int, 7)
        builder.add("pair2", A, x=7, y=7)
    
        self.testEntity = toyblock3.build_Entity(1, builder)
    
    def test1_entity_creation(self):
        
        @toyblock3.system("c")
        def c_system(system, entity):
            print(system, entity)
        
        builder = toyblock3.InstanceBuilder()
        builder.add('a', int)
        
        A = toyblock3.build_Entity(10, builder, self.a_system, c_system)
        self.assertTrue(len(A._entities) == 10)
        self.assertTrue(isinstance(A._entities[0], A))
        a = A.get()
        print("a", dir(a))
        a.free()
        b = A.get()
        self.assertTrue(a is b)
        self.assertTrue(self.a_system in A._systems)
        self.assertTrue(c_system._entities not in A._systems)
        self.a_system(7)
        c_system()
        
    def test2_entity_set(self):
        test = self.testEntity.get()
        test.set("pair", x=7, y=7)
        self.assertEqual(test.pair["x"], 7)
        self.assertEqual(test.pair["y"], 7)
        test.set("pair2", y=12)
        self.assertEqual(test.pair2.x, 7)
        self.assertEqual(test.pair2.y, 12)

    def test3_entity_initclean(self):
        
        @self.testEntity.init
        def init_12(entity):
            entity.set("pair2", x=12, y=12)
        
        @self.testEntity.clean
        def clean_12(entity):
            self.assertEqual(entity.pair2.x, 12)
            self.assertEqual(entity.pair2.y, 12)
            
        one = self.testEntity.get()
        
        self.assertEqual(one.pair2.x, 12)
        self.assertEqual(one.pair2.y, 12)
        
        one.free()

class TestEntityBuilder(unittest.TestCase):
    
    def test1_works_well(self):
        
        builder = toyblock3.InstanceBuilder()
        builder.add("id", int)
        builder.add("id2", int, 7)
        
        for entry in builder:
            print(entry)
        
        print(builder.components)
        
        self.assertEqual(builder.components, ("id", "id2"))
        
    def test2_full_example(self):
        
        @toyblock3.System("op1, op2")
        def suma(system, entity):
            my_sum = entity.op1 + entity.op2
            self.assertEqual(my_sum, 7)

        #table = toyblock3.factory(("op1", "op2", ))
