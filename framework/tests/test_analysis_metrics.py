import unittest
import ast
import tempfile
import os
from cop_python.analysis.metrics import (
    MetricsProvider, ComplexityMetricsProvider, SizeMetricsProvider,
    DependencyMetricsProvider, get_default_metrics_providers
)


class TestMetricsProvider(unittest.TestCase):
    """Test the base MetricsProvider class."""
    
    def test_base_class_interface(self):
        """Test that the base class defines the correct interface."""
        provider = MetricsProvider()
        
        with self.assertRaises(NotImplementedError):
            provider.calculate_metrics("function", ast.parse("pass"), "test.py")


class TestComplexityMetricsProvider(unittest.TestCase):
    """Test the ComplexityMetricsProvider class."""
    
    def setUp(self):
        """Set up test cases."""
        self.provider = ComplexityMetricsProvider()
    
    def test_simple_function(self):
        """Test complexity metrics for a simple function."""
        code = """
def simple_function():
    return True
"""
        tree = ast.parse(code)
        func_node = tree.body[0]
        
        metrics = self.provider.calculate_metrics("function", func_node, "test.py")
        
        # Simple function should have complexity of 1
        self.assertEqual(metrics["cyclomatic_complexity"], 1)
        self.assertEqual(metrics["cognitive_complexity"], 0)
    
    def test_function_with_if(self):
        """Test complexity metrics for a function with if statement."""
        code = """
def function_with_if(x):
    if x > 0:
        return True
    return False
"""
        tree = ast.parse(code)
        func_node = tree.body[0]
        
        metrics = self.provider.calculate_metrics("function", func_node, "test.py")
        
        # Function with one if should have cyclomatic complexity of 2
        self.assertEqual(metrics["cyclomatic_complexity"], 2)
        self.assertEqual(metrics["cognitive_complexity"], 1)
    
    def test_function_with_nested_if(self):
        """Test complexity metrics for a function with nested if statements."""
        code = """
def function_with_nested_if(x, y):
    if x > 0:
        if y > 0:
            return True
        return False
    return None
"""
        tree = ast.parse(code)
        func_node = tree.body[0]
        
        metrics = self.provider.calculate_metrics("function", func_node, "test.py")
        
        # Function with nested ifs should have higher cognitive complexity
        self.assertEqual(metrics["cyclomatic_complexity"], 3)
        # Cognitive complexity accounts for nesting: 1 + (1 + 1) = 3
        self.assertEqual(metrics["cognitive_complexity"], 3)
    
    def test_function_with_loop(self):
        """Test complexity metrics for a function with loops."""
        code = """
def function_with_loop(items):
    for item in items:
        if item > 0:
            return item
    return None
"""
        tree = ast.parse(code)
        func_node = tree.body[0]
        
        metrics = self.provider.calculate_metrics("function", func_node, "test.py")
        
        # Function with for loop and if should have complexity of 3
        self.assertEqual(metrics["cyclomatic_complexity"], 3)
        # Cognitive complexity: for (1) + if nested in for (1 + 1) = 3
        self.assertEqual(metrics["cognitive_complexity"], 3)
    
    def test_non_function_component(self):
        """Test that non-function components return empty metrics."""
        code = """
class TestClass:
    pass
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        
        metrics = self.provider.calculate_metrics("class", class_node, "test.py")
        
        # Classes should return empty metrics
        self.assertEqual(metrics, {})


class TestSizeMetricsProvider(unittest.TestCase):
    """Test the SizeMetricsProvider class."""
    
    def setUp(self):
        """Set up test cases."""
        self.provider = SizeMetricsProvider()
    
    def test_simple_function(self):
        """Test size metrics for a simple function."""
        code = """
def simple_function(a, b):
    '''Simple function docstring.'''
    x = a + b
    return x
"""
        tree = ast.parse(code)
        func_node = tree.body[0]
        
        # Mock line numbers
        func_node.lineno = 2
        func_node.end_lineno = 5
        
        metrics = self.provider.calculate_metrics("function", func_node, "test.py")
        
        self.assertEqual(metrics["lines_of_code"], 4)  # Lines 2-5
        self.assertEqual(metrics["parameter_count"], 2)  # a, b
        self.assertEqual(metrics["local_variable_count"], 1)  # x
        self.assertEqual(metrics["return_count"], 1)
        self.assertGreater(metrics["statement_count"], 0)
    
    def test_class_metrics(self):
        """Test size metrics for a class."""
        code = """
class TestClass:
    '''Test class.'''
    
    class_attr = "value"
    other_attr = 42
    
    def __init__(self):
        self.instance_attr = 1
    
    def method1(self):
        return True
    
    def method2(self):
        return False
"""
        tree = ast.parse(code)
        class_node = tree.body[0]
        
        # Mock line numbers
        class_node.lineno = 2
        class_node.end_lineno = 14
        
        metrics = self.provider.calculate_metrics("class", class_node, "test.py")
        
        self.assertEqual(metrics["lines_of_code"], 13)  # Lines 2-14
        self.assertEqual(metrics["method_count"], 3)  # __init__, method1, method2
        self.assertEqual(metrics["attribute_count"], 2)  # class_attr, other_attr
        self.assertGreater(metrics["statement_count"], 0)
    
    def test_function_with_local_variables(self):
        """Test counting local variables in a function."""
        code = """
def function_with_locals():
    a = 1
    b = 2
    for i in range(10):
        c = a + b + i
        with open("file") as f:
            d = f.read()
    return c + d
"""
        tree = ast.parse(code)
        func_node = tree.body[0]
        
        metrics = self.provider.calculate_metrics("function", func_node, "test.py")
        
        # Should count a, b, i, c, f, d
        self.assertEqual(metrics["local_variable_count"], 6)
        self.assertEqual(metrics["return_count"], 1)


class TestDependencyMetricsProvider(unittest.TestCase):
    """Test the DependencyMetricsProvider class."""
    
    def setUp(self):
        """Set up test cases."""
        self.provider = DependencyMetricsProvider()
    
    def test_module_imports(self):
        """Test dependency metrics for module imports."""
        code = """
import os
import sys
from collections import defaultdict
from typing import Dict, List
import external_package
"""
        tree = ast.parse(code)
        
        metrics = self.provider.calculate_metrics("module", tree, "test.py")
        
        # Should count all imports: os, sys, defaultdict, Dict, List, external_package
        self.assertEqual(metrics["import_count"], 6)  # os, sys, defaultdict, Dict, List, external_package
        self.assertEqual(metrics["external_dependency_count"], 1)  # external_package
    
    def test_function_calls(self):
        """Test function call counting."""
        code = """
def function_with_calls():
    result = some_function()
    another_call(1, 2, 3)
    obj.method_call()
    nested_call(other_call())
    return result
"""
        tree = ast.parse(code)
        func_node = tree.body[0]
        
        metrics = self.provider.calculate_metrics("function", func_node, "test.py")
        
        # Should count all function calls
        self.assertEqual(metrics["function_call_count"], 5)
    
    def test_stdlib_detection(self):
        """Test standard library module detection."""
        # Test known stdlib modules
        self.assertTrue(self.provider._is_stdlib("os"))
        self.assertTrue(self.provider._is_stdlib("sys"))
        self.assertTrue(self.provider._is_stdlib("json"))
        self.assertTrue(self.provider._is_stdlib("collections"))
        
        # Test private modules (should be considered stdlib)
        self.assertTrue(self.provider._is_stdlib("_ast"))
        self.assertTrue(self.provider._is_stdlib("_collections"))
        
        # Test non-stdlib modules
        self.assertFalse(self.provider._is_stdlib("numpy"))
        self.assertFalse(self.provider._is_stdlib("requests"))
        self.assertFalse(self.provider._is_stdlib("external_package"))


class TestDefaultMetricsProviders(unittest.TestCase):
    """Test the default metrics providers function."""
    
    def test_get_default_providers(self):
        """Test that default providers are returned correctly."""
        providers = get_default_metrics_providers()
        
        # Should return all three provider types
        self.assertEqual(len(providers), 3)
        
        # Check types
        provider_types = [type(p).__name__ for p in providers]
        self.assertIn("ComplexityMetricsProvider", provider_types)
        self.assertIn("SizeMetricsProvider", provider_types)
        self.assertIn("DependencyMetricsProvider", provider_types)


if __name__ == "__main__":
    unittest.main()