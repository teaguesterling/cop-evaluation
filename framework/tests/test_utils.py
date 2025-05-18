# tests/test_utils.py
import unittest
import sys
from cop_python.runtime import enable_cop, disable_cop, get_system
from cop_python.annotations import (
    intent, implementation_status, risk, invariant, decision,
    IMPLEMENTED, PARTIAL, NOT_IMPLEMENTED
)
from cop_python.utils import (
    register_annotation, get_annotations, find_annotation,
    get_implementation_status, get_intent, get_risks,
    has_annotation, resolve_component
)

class TestAnnotationUtilities(unittest.TestCase):
    """Test the annotation utility functions."""
    
    def setUp(self):
        enable_cop()
        
    def tearDown(self):
        disable_cop()
        
    def test_register_annotation(self):
        """Test registering an annotation on a component."""
        # Create a test function
        def test_function(): pass
        
        # Register an annotation
        result = register_annotation(intent, test_function, "Test intent")
        
        # Result should be the function
        self.assertIs(result, test_function)
        
        # Function should have the intent annotation
        self.assertTrue(hasattr(test_function, "__cop_annotations__"))
        annotations = test_function.__cop_annotations__.intent
        self.assertEqual(len(annotations), 1)
        self.assertEqual(annotations[0].value, "Test intent")
        
    def test_get_annotations(self):
        """Test getting annotations from an object."""
        # Create a test function with annotations
        @intent("Test intent")
        @implementation_status(IMPLEMENTED)
        def test_function(): pass
        
        # Get all annotations
        annotations = get_annotations(test_function)
        
        # Should have two annotations
        self.assertEqual(len(annotations), 2)
        
        # Get intent annotations
        intent_annotations = get_annotations(test_function, "intent")
        self.assertEqual(len(intent_annotations), 1)
        self.assertEqual(intent_annotations[0].value, "Test intent")
        
    def test_find_annotation(self):
        """Test finding a specific annotation."""
        # Create a test function with a risk annotation
        @risk("Security risk", severity="HIGH")
        def test_function(): pass
        
        # Find the annotation
        annotation = find_annotation(test_function, "risk", "Security risk", severity="HIGH")
        
        # Should find the annotation
        self.assertIsNotNone(annotation)
        self.assertEqual(annotation.value, "Security risk")
        self.assertEqual(annotation.metadata.get("severity"), "HIGH")
        
        # Try to find an annotation that doesn't exist
        not_found = find_annotation(test_function, "risk", "Other risk")
        self.assertIsNone(not_found)
        
    def test_get_implementation_status(self):
        """Test getting implementation status."""
        # Create a test function with implementation status
        @implementation_status(IMPLEMENTED)
        def test_function(): pass
        
        # Get the status
        status = get_implementation_status(test_function)
        
        # Should be IMPLEMENTED
        self.assertEqual(status.value, IMPLEMENTED)
        
        # Function without status should return default
        def no_status_function(): pass
        status = get_implementation_status(no_status_function, default=NOT_IMPLEMENTED)
        self.assertEqual(status, NOT_IMPLEMENTED)
        
    def test_get_intent(self):
        """Test getting intent."""
        # Create a test function with intent
        @intent("Test intent")
        def test_function(): pass
        
        # Get the intent
        result = get_intent(test_function)
        
        # Should be the intent annotation
        self.assertEqual(result.value, "Test intent")
        
    def test_get_risks(self):
        """Test getting risks."""
        # Create a test function with risks
        @risk("Security risk", category="security", severity="HIGH")
        @risk("Performance risk", category="performance", severity="MEDIUM")
        def test_function(): pass
        
        # Get all risks
        risks = get_risks(test_function)
        self.assertEqual(len(risks), 2)
        
        # Get security risks
        security_risks = get_risks(test_function, category_in=["security"])
        self.assertEqual(len(security_risks), 1)
        self.assertEqual(security_risks[0].value, "Security risk")
        
    def test_has_annotation(self):
        """Test checking if an object has an annotation."""
        # Create a test function with an annotation
        @intent("Test intent")
        def test_function(): pass
        
        # Check for intent
        self.assertTrue(has_annotation(test_function, "intent"))
        
        # Check for specific intent
        self.assertTrue(has_annotation(test_function, "intent", "Test intent"))
        
        # Check for non-existent annotation
        self.assertFalse(has_annotation(test_function, "risk"))
        
    def test_resolve_component(self):
        """Test resolving a component from a string path."""
        # Define a test module in sys.modules
        class TestModule:
            pass
            
        class TestComponent:
            pass
            
        TestModule.test_component = TestComponent
        sys.modules["test_module"] = TestModule
        
        try:
            # Resolve from string path
            resolved = resolve_component("test_module.test_component")
            
            # Should resolve to the component
            self.assertIs(resolved, TestComponent)
            
            # Already resolved component should be returned as-is
            self.assertIs(resolve_component(TestComponent), TestComponent)
            
            # Non-existent component should raise ValueError
            with self.assertRaises(ValueError):
                resolve_component("test_module.non_existent")
                
        finally:
            # Clean up
            del sys.modules["test_module"]

if __name__ == "__main__":
    unittest.main()
