import unittest
from cop_python.runtime import enable_cop, disable_cop, get_system, DISABLED
from cop_python.core import (
    COPAnnotation, COPSingletonAnnotation, 
    DuplicateAnnotationError, ConceptAnnotations,
    COPAnnotationData, _do_nothing_decorator
)

class TestCOPAnnotation(unittest.TestCase):
    """Test the COPAnnotation base class."""
    
    def setUp(self):
        # Enable COP for these tests
        enable_cop()
        
    def tearDown(self):
        # Disable COP after tests
        disable_cop()

    def test_ensure_enabled(self):
        self.assertTrue(get_system().is_enabled())
        self.assertTrue(get_system() is not DISABLED)
        
    def test_creation(self):
        """Test creating an annotation."""
        # Create a test annotation class
        class TestAnnotation(COPAnnotation):
            annotation_type = "test_annotation"
            
        # Create an annotation
        annotation = TestAnnotation("test_value", param="test_param")
        
        # Check properties
        self.assertEqual(annotation.value, "test_value")
        self.assertEqual(annotation.metadata["param"], "test_param")
        
    def test_kind(self):
        """Test the kind property."""
        class TestAnnotation(COPAnnotation):
            annotation_type = "test_annotation"
            
        annotation = TestAnnotation("test_value")
        self.assertEqual(annotation.kind, "test_annotation")
        
        # If annotation_type is not set, should use class name
        class NoTypeAnnotation(COPAnnotation):
            pass
            
        no_type = NoTypeAnnotation("test_value")
        self.assertEqual(no_type.kind, "NoTypeAnnotation")
        
    def test_application_to_object(self):
        """Test applying an annotation to an object."""
        class TestAnnotation(COPAnnotation):
            annotation_type = "test_annotation"
            
        # Create a test object
        class TestObject:
            pass
            
        obj = TestObject()
        
        # Apply annotation
        annotation = TestAnnotation("test_value")
        result = annotation(obj)
        
        # Result should be the object
        self.assertIs(result, obj)
        
        # Object should have __cop_annotations__ attribute
        self.assertTrue(hasattr(obj, "__cop_annotations__"))
        
        # Annotations should include our annotation
        annotations = obj.__cop_annotations__.test_annotation
        self.assertEqual(len(annotations), 1)
        self.assertEqual(annotations[0].value, "test_value")
        
    def test_context_manager(self):
        """Test using an annotation as a context manager."""
        class TestAnnotation(COPAnnotation):
            annotation_type = "test_annotation"
            
        # Use as context manager
        with TestAnnotation("test_value") as annotation:
            # Should push context
            contexts = get_system().get_contexts("test_annotation")
            self.assertEqual(len(contexts), 1)
            self.assertEqual(contexts[0].value, "test_value")
            
        # After context ends, should pop context
        contexts = get_system().get_contexts("test_annotation")
        self.assertEqual(len(contexts), 0)
        
    def test_disabled_behavior(self):
        """Test behavior when COP is disabled."""
        # Disable COP
        disable_cop()
        
        class TestAnnotation(COPAnnotation):
            annotation_type = "test_annotation"
            
        # Create annotation (should return _do_nothing_decorator)
        annotation = TestAnnotation("test_value")
        self.assertIs(annotation, _do_nothing_decorator)
        
        # Apply to object (should return object unchanged)
        obj = object()
        result = annotation(obj)
        self.assertIs(result, obj)
        
        # Use as context manager (should be no-op)
        with annotation as ctx:
            self.assertIs(ctx, annotation)
            # No contexts should be pushed
            contexts = get_system().get_contexts("test_annotation")
            self.assertEqual(len(contexts), 0)

class TestCOPSingletonAnnotation(unittest.TestCase):
    """Test the COPSingletonAnnotation class."""
    
    def setUp(self):
        enable_cop()
        
    def tearDown(self):
        disable_cop()
        
    def test_singleton_behavior(self):
        """Test that only one singleton annotation can be applied."""
        class TestSingleton(COPSingletonAnnotation):
            annotation_type = "test_singleton"
            
        # Create a test object
        class TestObject:
            pass
            
        obj = TestObject()
        
        # Apply first annotation (should work)
        TestSingleton("first")(obj)
        
        # Apply second annotation (should raise error)
        with self.assertRaises(DuplicateAnnotationError):
            TestSingleton("second")(obj)
            
class TestConceptAnnotations(unittest.TestCase):
    """Test the ConceptAnnotations collection."""
    
    def setUp(self):
        enable_cop()
        
    def tearDown(self):
        disable_cop()
        
    def test_collection_behavior(self):
        """Test the collection behavior."""
        # Create test annotations
        class TestAnnotation(COPAnnotation):
            annotation_type = "test_annotation"
            
        anno1 = TestAnnotation("value1")
        anno2 = TestAnnotation("value2")
        
        # Create a collection
        collection = ConceptAnnotations([anno1, anno2])
        
        # Should behave like a list
        self.assertEqual(len(collection), 2)
        self.assertEqual(collection[0], anno1)
        self.assertEqual(collection[1], anno2)
        
    def test_apply_to(self):
        """Test applying all annotations to an object."""
        # Create test annotations
        class TestAnnotation(COPAnnotation):
            annotation_type = "test_annotation"
            
        anno1 = TestAnnotation("value1")
        anno2 = TestAnnotation("value2")
        
        # Create a collection
        collection = ConceptAnnotations([anno1, anno2])
        
        # Create a test object
        class TestObject:
            pass
            
        obj = TestObject()
        
        # Apply annotations
        result = collection.apply_to(obj)
        
        # Result should be the object
        self.assertIs(result, obj)
        
        # Object should have both annotations
        annotations = obj.__cop_annotations__.test_annotation
        self.assertEqual(len(annotations), 2)
        self.assertEqual(annotations[0].value, "value1")
        self.assertEqual(annotations[1].value, "value2")
        
    def test_context_manager(self):
        """Test using the collection as a context manager."""
        # Create test annotation class
        class TestAnnotation(COPAnnotation):
            annotation_type = "test_annotation"
            
        # Create a system to track annotations
        system = get_system()
        
        # Use as context manager
        with ConceptAnnotations() as collection:
            # Create an annotation during the context
            anno = TestAnnotation("dynamic")
            
            # Should be in the collection
            self.assertEqual(len(collection), 1)
            self.assertEqual(collection[0].value, "dynamic")

if __name__ == "__main__":
    unittest.main()
