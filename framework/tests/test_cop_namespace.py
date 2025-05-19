"""Tests for COPNamespace functionality."""

import unittest
from cop_python.runtime import COPNamespace, enable_cop, disable_cop
from cop_python.core import ConceptAnnotations


class TestCOPNamespace(unittest.TestCase):
    """Test the COPNamespace class."""
    
    def setUp(self):
        enable_cop()
    
    def tearDown(self):
        disable_cop()
    
    def test_keys_method_returns_annotation_types(self):
        """Test that keys() returns only the annotation type attributes (not methods)."""
        namespace = COPNamespace(default_factory=ConceptAnnotations)
        
        # Add some annotation types
        namespace.invariant = ConceptAnnotations([])
        namespace.risk = ConceptAnnotations([])
        
        # keys() should return only the annotation types
        keys = namespace.keys()
        self.assertIn("invariant", keys)
        self.assertIn("risk", keys)
        
        # Should not include methods
        self.assertNotIn("get", keys)
        self.assertNotIn("items", keys)
        self.assertNotIn("values", keys)
        self.assertNotIn("keys", keys)
    
    def test_values_method_returns_annotation_lists(self):
        """Test that values() returns only the annotation lists."""
        namespace = COPNamespace(default_factory=ConceptAnnotations)
        
        # Add some annotation types
        namespace.invariant = ConceptAnnotations([])
        namespace.risk = ConceptAnnotations([])
        
        # values() should return the lists
        values = namespace.values()
        self.assertEqual(len(values), 2)
        for value in values:
            self.assertIsInstance(value, ConceptAnnotations)
    
    def test_items_method_returns_pairs(self):
        """Test that items() returns (type, annotations) pairs."""
        namespace = COPNamespace(default_factory=ConceptAnnotations)
        
        # Add some annotation types
        namespace.invariant = ConceptAnnotations([])
        namespace.risk = ConceptAnnotations([])
        
        # items() should return pairs
        items = namespace.items()
        self.assertEqual(len(items), 2)
        
        # Convert to dict for easier testing
        items_dict = dict(items)
        self.assertIn("invariant", items_dict)
        self.assertIn("risk", items_dict)
        self.assertIsInstance(items_dict["invariant"], ConceptAnnotations)
        self.assertIsInstance(items_dict["risk"], ConceptAnnotations)
    
    def test_iteration_over_namespace(self):
        """Test that we can iterate over a COPNamespace to get annotation types."""
        namespace = COPNamespace(default_factory=ConceptAnnotations)
        
        # Add some annotation types
        namespace.invariant = ConceptAnnotations([])
        namespace.risk = ConceptAnnotations([])
        namespace.intent = ConceptAnnotations([])
        
        # Should be able to iterate over it
        annotation_types = list(namespace)
        self.assertEqual(len(annotation_types), 3)
        self.assertIn("invariant", annotation_types)
        self.assertIn("risk", annotation_types)
        self.assertIn("intent", annotation_types)
    
    def test_getitem_access(self):
        """Test dictionary-style access via __getitem__."""
        namespace = COPNamespace(default_factory=ConceptAnnotations)
        
        # Access via __getitem__ should create new ConceptAnnotations if needed
        inv = namespace["invariant"]
        self.assertIsInstance(inv, ConceptAnnotations)
        
        # Should be the same object as attribute access
        self.assertIs(inv, namespace.invariant)
    
    def test_keys_filters_correctly(self):
        """Test that keys() only returns attributes that are lists (not methods)."""
        namespace = COPNamespace(default_factory=ConceptAnnotations)
        
        # Add different types of attributes
        namespace.invariant = ConceptAnnotations([])
        namespace.some_method = lambda: None  # Add a method
        namespace.some_string = "test"  # Add a string
        namespace.some_number = 42  # Add a number
        
        # keys() should only return list attributes
        keys = namespace.keys()
        self.assertIn("invariant", keys)
        self.assertNotIn("some_method", keys)
        self.assertNotIn("some_string", keys)
        self.assertNotIn("some_number", keys)
    
    def test_contains_method(self):
        """Test the __contains__ method for checking attribute existence."""
        namespace = COPNamespace(default_factory=ConceptAnnotations)
        
        # Add an annotation type
        namespace.invariant = ConceptAnnotations([])
        
        # Should contain the annotation type
        self.assertIn("invariant", namespace)
        
        # Should not contain non-existent types
        self.assertNotIn("nonexistent", namespace)
        
        # Should not contain private attributes
        self.assertNotIn("_private", namespace)


if __name__ == "__main__":
    unittest.main()