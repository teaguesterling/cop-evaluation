"""Tests for new utility functions in cop_python.utils."""

import unittest
from cop_python.runtime import enable_cop, disable_cop, COPNamespace
from cop_python.core import ConceptAnnotations
from cop_python.utils import (
    get_annotations_namespace,
    get_all_annotations,
    get_all_annotations_dict
)
import cop_python.annotations as cop_annotations


class TestNewUtilityFunctions(unittest.TestCase):
    """Test the new utility functions."""
    
    def setUp(self):
        enable_cop()
    
    def tearDown(self):
        disable_cop()
    
    def test_get_annotations_namespace_with_annotations(self):
        """Test getting namespace from an object with annotations."""
        @cop_annotations.invariant("Must be positive")
        @cop_annotations.risk("Security risk", severity="HIGH")
        def test_func(x):
            return x > 0
        
        namespace = get_annotations_namespace(test_func)
        
        # Should be a COPNamespace
        self.assertIsInstance(namespace, COPNamespace)
        
        # Should have the expected annotations
        self.assertIn("invariant", namespace.keys())
        self.assertIn("risk", namespace.keys())
        
        # Check the annotations
        self.assertEqual(len(namespace.invariant), 1)
        self.assertEqual(namespace.invariant[0].value, "Must be positive")
        
        self.assertEqual(len(namespace.risk), 1)
        self.assertEqual(namespace.risk[0].value, "Security risk")
        self.assertEqual(namespace.risk[0].metadata["severity"], "HIGH")
    
    def test_get_annotations_namespace_without_annotations(self):
        """Test getting namespace from an object without annotations."""
        def plain_func():
            pass
        
        namespace = get_annotations_namespace(plain_func)
        
        # Should be an empty COPNamespace
        self.assertIsInstance(namespace, COPNamespace)
        self.assertEqual(len(namespace.keys()), 0)
    
    def test_get_all_annotations(self):
        """Test getting all annotations as a flat list."""
        @cop_annotations.invariant("Must be positive")
        @cop_annotations.risk("Security risk", severity="HIGH")
        @cop_annotations.implementation_status(cop_annotations.IMPLEMENTED)
        def test_func(x):
            return x > 0
        
        all_annotations = get_all_annotations(test_func)
        
        # Should be a ConceptAnnotations object
        self.assertIsInstance(all_annotations, ConceptAnnotations)
        
        # Should have 3 annotations
        self.assertEqual(len(all_annotations), 3)
        
        # Check that we have all types
        annotation_types = {anno.kind for anno in all_annotations}
        self.assertEqual(annotation_types, {"invariant", "risk", "implementation_status"})
    
    def test_get_all_annotations_empty(self):
        """Test getting all annotations from an object without annotations."""
        def plain_func():
            pass
        
        all_annotations = get_all_annotations(plain_func)
        
        # Should be an empty ConceptAnnotations object
        self.assertIsInstance(all_annotations, ConceptAnnotations)
        self.assertEqual(len(all_annotations), 0)
    
    def test_get_all_annotations_dict(self):
        """Test getting all annotations as a dictionary."""
        @cop_annotations.invariant("Must be positive")
        @cop_annotations.invariant("Must be less than 100")
        @cop_annotations.risk("Security risk", severity="HIGH")
        @cop_annotations.decision("Use caching", priority="HIGH")
        def test_func(x):
            return 0 < x < 100
        
        annotations_dict = get_all_annotations_dict(test_func)
        
        # Should be a dictionary
        self.assertIsInstance(annotations_dict, dict)
        
        # Should have 3 types
        self.assertEqual(len(annotations_dict), 3)
        self.assertIn("invariant", annotations_dict)
        self.assertIn("risk", annotations_dict)
        self.assertIn("decision", annotations_dict)
        
        # Each value should be a ConceptAnnotations object
        for value in annotations_dict.values():
            self.assertIsInstance(value, ConceptAnnotations)
        
        # Check invariants (should have 2)
        self.assertEqual(len(annotations_dict["invariant"]), 2)
        invariant_values = [anno.value for anno in annotations_dict["invariant"]]
        self.assertIn("Must be positive", invariant_values)
        self.assertIn("Must be less than 100", invariant_values)
        
        # Check risk (should have 1)
        self.assertEqual(len(annotations_dict["risk"]), 1)
        self.assertEqual(annotations_dict["risk"][0].value, "Security risk")
        
        # Check decision (should have 1)
        self.assertEqual(len(annotations_dict["decision"]), 1)
        self.assertEqual(annotations_dict["decision"][0].value, "Use caching")
    
    def test_get_all_annotations_dict_empty(self):
        """Test getting all annotations dict from an object without annotations."""
        def plain_func():
            pass
        
        annotations_dict = get_all_annotations_dict(plain_func)
        
        # Should be an empty dictionary
        self.assertIsInstance(annotations_dict, dict)
        self.assertEqual(len(annotations_dict), 0)
    
    def test_utility_functions_with_class(self):
        """Test utility functions with a class."""
        @cop_annotations.intent("Handles user authentication")
        class UserAuth:
            @cop_annotations.invariant("Password must be hashed")
            def set_password(self, password):
                pass
            
            @cop_annotations.risk("Session hijacking", severity="MEDIUM")
            def create_session(self):
                pass
        
        # Test with class
        class_namespace = get_annotations_namespace(UserAuth)
        self.assertIn("intent", class_namespace.keys())
        
        class_annotations = get_all_annotations(UserAuth)
        self.assertEqual(len(class_annotations), 1)
        self.assertEqual(class_annotations[0].value, "Handles user authentication")
        
        # Test with method
        method_annotations = get_all_annotations_dict(UserAuth.set_password)
        self.assertIn("invariant", method_annotations)
        self.assertEqual(len(method_annotations["invariant"]), 1)
        self.assertEqual(method_annotations["invariant"][0].value, "Password must be hashed")


if __name__ == "__main__":
    unittest.main()