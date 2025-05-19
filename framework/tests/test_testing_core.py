"""Tests for cop_python.testing.core module."""

import unittest
import inspect
from cop_python.runtime import enable_cop, disable_cop, get_system
from cop_python.testing.foundation import (
    # Exception classes
    COPAnnotationViolation,
    InvariantViolation,
    RiskViolation,
    ImplementationStatusMismatch,
    DecisionViolation,
    IntentViolation,
    
    # Data structures
    COPTestData,
    
    # Context manager/decorator
    tests_concept,
    
    # Utility functions
    get_current_component,
    set_current_annotation_type,
    get_current_annotation_type,
    get_test_id
)
from cop_python.utils import COPAnnotationReference


class TestExceptionClasses(unittest.TestCase):
    """Test custom exception classes."""
    
    def test_exception_hierarchy(self):
        """Test that all exceptions inherit from COPAnnotationViolation."""
        self.assertTrue(issubclass(InvariantViolation, COPAnnotationViolation))
        self.assertTrue(issubclass(RiskViolation, COPAnnotationViolation))
        self.assertTrue(issubclass(ImplementationStatusMismatch, COPAnnotationViolation))
        self.assertTrue(issubclass(DecisionViolation, COPAnnotationViolation))
        self.assertTrue(issubclass(IntentViolation, COPAnnotationViolation))
        
    def test_cop_annotation_violation_is_assertion_error(self):
        """Test that COPAnnotationViolation is an AssertionError."""
        self.assertTrue(issubclass(COPAnnotationViolation, AssertionError))
        
    def test_exception_instantiation(self):
        """Test that exceptions can be instantiated with messages."""
        exc = InvariantViolation("Test invariant violation")
        self.assertEqual(str(exc), "Test invariant violation")
        
        exc = RiskViolation("Security breach")
        self.assertEqual(str(exc), "Security breach")


class TestCOPTestData(unittest.TestCase):
    """Test the COPTestData structure."""
    
    def setUp(self):
        enable_cop()
        
    def tearDown(self):
        disable_cop()
    
    def test_cop_test_data_creation(self):
        """Test creating a COPTestData instance."""
        annotation_ref = COPAnnotationReference(
            annotation_type="invariant",
            annotation_value="Must be positive",
            metadata_keys={"critical": True}
        )
        
        test_data = COPTestData(
            test_id="test_module.test_function",
            annotation_reference=annotation_ref,
            test_metadata={"priority": "high"},
            source_info=None
        )
        
        self.assertEqual(test_data.test_id, "test_module.test_function")
        self.assertEqual(test_data.annotation_reference, annotation_ref)
        self.assertEqual(test_data.test_metadata, {"priority": "high"})
        self.assertIsNone(test_data.source_info)
        
    def test_cop_test_data_to_dict(self):
        """Test converting COPTestData to dictionary."""
        annotation_ref = COPAnnotationReference(
            annotation_type="risk",
            annotation_value="Security risk",
            metadata_keys={"severity": "HIGH"}
        )
        
        test_data = COPTestData(
            test_id="test_module.TestClass.test_method",
            annotation_reference=annotation_ref,
            test_metadata={"category": "security"},
            source_info=None
        )
        
        result = test_data.to_dict()
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["test_id"], "test_module.TestClass.test_method")
        self.assertIn("annotation_reference", result)
        self.assertEqual(result["test_metadata"], {"category": "security"})


class TestTestsConcept(unittest.TestCase):
    """Test the tests_concept context manager and decorator."""
    
    def setUp(self):
        enable_cop()
        
    def tearDown(self):
        disable_cop()
        
    def test_component_setup():
        """Test a simple function we'll use in tests."""
        pass
        
    def test_context_manager_usage(self):
        """Test using tests_concept as a context manager."""
        # Check no component is set initially
        self.assertIsNone(get_current_component())
        
        # Use as context manager
        with tests_concept(self.test_component_setup):
            # Component should be available inside context
            self.assertEqual(get_current_component(), self.test_component_setup)
            
        # Component should be cleared after context
        self.assertIsNone(get_current_component())
        
    def test_function_decorator(self):
        """Test using tests_concept as a function decorator."""
        @tests_concept(self.test_component_setup)
        def test_function():
            # Inside the test function, component should be available
            return get_current_component()
            
        # Call the decorated function
        result = test_function()
        self.assertEqual(result, self.test_component_setup)
        
        # Component should be available as attribute on function
        self.assertEqual(test_function.__cop_concept_component__, self.test_component_setup)
        
    def test_class_decorator(self):
        """Test using tests_concept as a class decorator."""
        @tests_concept(self.test_component_setup)
        class TestClass:
            def test_method(self):
                return get_current_component()
                
        # Create instance and call test method
        instance = TestClass()
        
        # setUp should be called to set component
        if hasattr(instance, 'setUp'):
            instance.setUp()
            
        # Component should be available
        self.assertEqual(instance.concept, self.test_component_setup)
        
        # Component should be available as class attribute
        self.assertEqual(TestClass.__cop_concept_component__, self.test_component_setup)


class TestUtilityFunctions(unittest.TestCase):
    """Test utility functions."""
    
    def setUp(self):
        enable_cop()
        
    def tearDown(self):
        disable_cop()
        
    def test_get_current_component(self):
        """Test getting current component."""
        # Initially should be None
        self.assertIsNone(get_current_component())
        
        # Push a component to context
        test_component = lambda: None  # Simple test component
        get_system().push_context("test_component", test_component)
        
        # Should now return the component
        self.assertEqual(get_current_component(), test_component)
        
        # Clean up
        get_system().pop_context("test_component")
        self.assertIsNone(get_current_component())
        
    def test_annotation_type_context(self):
        """Test setting and getting annotation type context."""
        # Initially should be None
        self.assertIsNone(get_current_annotation_type())
        
        # Set annotation type
        set_current_annotation_type("invariant")
        self.assertEqual(get_current_annotation_type(), "invariant")
        
        # Set another type
        set_current_annotation_type("risk")
        self.assertEqual(get_current_annotation_type(), "risk")
        
        # Clean up
        get_system().pop_context("test_annotation_type")
        get_system().pop_context("test_annotation_type")
        self.assertIsNone(get_current_annotation_type())
        
    def test_get_test_id(self):
        """Test generating test IDs."""
        # Test with a simple function
        def simple_test():
            pass
            
        test_id = get_test_id(simple_test)
        self.assertEqual(test_id, f"{simple_test.__module__}.simple_test")
        
        # Test with a class method
        class TestClass:
            def test_method(self):
                pass
                
        # For unbound methods, we can't determine the class
        test_id = get_test_id(TestClass.test_method)
        expected = f"{TestClass.test_method.__module__}.test_method"
        self.assertEqual(test_id, expected)
        
    def test_nested_contexts(self):
        """Test nested component contexts."""
        component1 = lambda: "Component 1"
        component2 = lambda: "Component 2"
        
        # Initially None
        self.assertIsNone(get_current_component())
        
        # First context
        get_system().push_context("test_component", component1)
        self.assertEqual(get_current_component(), component1)
        
        # Nested context
        get_system().push_context("test_component", component2)
        self.assertEqual(get_current_component(), component2)
        
        # Pop inner context
        get_system().pop_context("test_component")
        self.assertEqual(get_current_component(), component1)
        
        # Pop outer context
        get_system().pop_context("test_component")
        self.assertIsNone(get_current_component())


if __name__ == "__main__":
    unittest.main()