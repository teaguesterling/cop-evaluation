import unittest
import os
import ast
import tempfile
from typing import List, Dict, Any
from cop_python.analysis.extractor import (
    AnnotationInfo, COPAnnotationVisitor, 
    extract_annotations_from_file, extract_annotations_from_directory
)

class TestAnnotationInfo(unittest.TestCase):
    """Test the AnnotationInfo class."""
    
    def test_annotation_info_structure(self):
        """Test that AnnotationInfo has the correct fields."""
        # Create a sample annotation
        annotation = AnnotationInfo(
            annotation_type="intent",
            component_name="test.component",
            component_type="function",
            file_path="/path/to/file.py",
            line_number=10,
            value="Test Intent",
            metadata={"key": "value"},
            component_info={"docstring": "Test docstring"},
            start_line=8,
            end_line=15,
            actual_start_line=10
        )
        
        # Verify all fields
        self.assertEqual(annotation.annotation_type, "intent")
        self.assertEqual(annotation.component_name, "test.component")
        self.assertEqual(annotation.component_type, "function")
        self.assertEqual(annotation.file_path, "/path/to/file.py")
        self.assertEqual(annotation.line_number, 10)
        self.assertEqual(annotation.value, "Test Intent")
        self.assertEqual(annotation.metadata, {"key": "value"})
        self.assertEqual(annotation.component_info, {"docstring": "Test docstring"})
        self.assertEqual(annotation.start_line, 8)
        self.assertEqual(annotation.end_line, 15)
        self.assertEqual(annotation.actual_start_line, 10)


class TestCOPAnnotationVisitor(unittest.TestCase):
    """Test the COPAnnotationVisitor class."""
    
    def setUp(self):
        """Set up test cases with sample code."""
        self.sample_code = '''
"""Sample module docstring."""

import os
import sys
from typing import List, Dict

@intent("Sample function")
@implementation_status("IMPLEMENTED")
def sample_function(a: int, b: str) -> List[Dict]:
    """Sample function docstring."""
    return [{"value": a + len(b)}]

@intent("Sample class")
@risk("Sample risk", severity="low")
class SampleClass:
    """Sample class docstring."""
    
    class_attr = "value"
    
    def __init__(self):
        self.instance_attr = 42
    
    @intent("Sample method")
    @invariant("Always true")
    def sample_method(self, a, b=None, *args, **kwargs):
        """Sample method docstring."""
        return True
'''
        self.file_path = "/path/to/sample.py"
        self.visitor = COPAnnotationVisitor(self.file_path, self.sample_code)
        # Parse and visit the AST
        tree = ast.parse(self.sample_code)
        self.visitor.visit(tree)
    
    def test_annotation_extraction(self):
        """Test that annotations are correctly extracted."""
        # Should have extracted 5 annotations: 
        # - intent on function
        # - implementation_status on function
        # - intent on class
        # - risk on class
        # - intent on method
        # - invariant on method
        self.assertEqual(len(self.visitor.annotations), 6)
        
        # Verify annotation types
        annotation_types = [a.annotation_type for a in self.visitor.annotations]
        self.assertEqual(annotation_types.count("intent"), 3)
        self.assertEqual(annotation_types.count("implementation_status"), 1)
        self.assertEqual(annotation_types.count("risk"), 1)
        self.assertEqual(annotation_types.count("invariant"), 1)
    
    def test_component_info_extraction(self):
        """Test that component information is correctly extracted."""
        # Find the function annotation
        function_anno = next((a for a in self.visitor.annotations 
                            if a.component_type == "function"), None)
        self.assertIsNotNone(function_anno)
        
        # Check function component info
        self.assertIn("docstring", function_anno.component_info)
        self.assertEqual(function_anno.component_info["docstring"], "Sample function docstring.")
        self.assertIn("params", function_anno.component_info)
        self.assertEqual(len(function_anno.component_info["params"]), 2)
        self.assertEqual(function_anno.component_info["params"][0]["name"], "a")
        self.assertEqual(function_anno.component_info["params"][0]["annotation"], "int")
        
        # Find the class annotation
        class_anno = next((a for a in self.visitor.annotations 
                          if a.component_type == "class"), None)
        self.assertIsNotNone(class_anno)
        
        # Check class component info
        self.assertIn("docstring", class_anno.component_info)
        self.assertEqual(class_anno.component_info["docstring"], "Sample class docstring.")
        self.assertIn("methods", class_anno.component_info)
        self.assertIn("__init__", class_anno.component_info["methods"])
        self.assertIn("sample_method", class_anno.component_info["methods"])
        self.assertIn("attributes", class_anno.component_info)
        self.assertIn("class_attr", class_anno.component_info["attributes"])
    
    def test_line_range_extraction(self):
        """Test that line ranges are correctly extracted."""
        # Check function line range
        function_anno = next((a for a in self.visitor.annotations 
                             if a.component_type == "function"), None)
        self.assertIsNotNone(function_anno)
        self.assertTrue(function_anno.start_line < function_anno.actual_start_line)
        self.assertTrue(function_anno.actual_start_line < function_anno.end_line)
        
        # Check method line range
        method_anno = next((a for a in self.visitor.annotations 
                           if "sample_method" in a.component_name), None)
        self.assertIsNotNone(method_anno)
        self.assertTrue(method_anno.start_line < method_anno.actual_start_line)
        self.assertTrue(method_anno.actual_start_line < method_anno.end_line)


class TestExtractAnnotations(unittest.TestCase):
    """Test the annotation extraction functions."""
    
    def setUp(self):
        """Create temporary files for testing."""
        # Create a temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Create a sample file
        self.sample_code = '''
@intent("Test function")
@implementation_status("IMPLEMENTED")
def test_function():
    """Test function."""
    return True

@intent("Test class")
class TestClass:
    """Test class."""
    
    @intent("Test method")
    def test_method(self):
        """Test method."""
        return True
'''
        self.file_path = os.path.join(self.temp_dir.name, "test_file.py")
        with open(self.file_path, 'w') as f:
            f.write(self.sample_code)
            
        # Create a second file for directory testing
        self.second_file_path = os.path.join(self.temp_dir.name, "test_file2.py")
        with open(self.second_file_path, 'w') as f:
            f.write('''
@intent("Second file function")
def second_function():
    """Second file function."""
    return True
''')
    
    def tearDown(self):
        """Clean up temporary files."""
        self.temp_dir.cleanup()
    
    def test_extract_annotations_from_file(self):
        """Test extracting annotations from a file."""
        annotations = extract_annotations_from_file(self.file_path)
        
        # Should have 4 annotations
        self.assertEqual(len(annotations), 4)
        
        # Verify component names
        component_names = [a.component_name for a in annotations]
        self.assertIn("test_file.test_function", component_names)
        self.assertIn("test_file.TestClass", component_names)
        self.assertIn("test_file.TestClass.test_method", component_names)
    
    def test_extract_annotations_from_directory(self):
        """Test extracting annotations from a directory."""
        annotations = extract_annotations_from_directory(self.temp_dir.name)
        
        # Should have 5 annotations (4 from first file + 1 from second)
        self.assertEqual(len(annotations), 5)
        
        # Verify component names from both files
        component_names = [a.component_name for a in annotations]
        self.assertIn("test_file.test_function", component_names)
        self.assertIn("test_file.TestClass", component_names)
        self.assertIn("test_file.TestClass.test_method", component_names)
        self.assertIn("test_file2.second_function", component_names)


if __name__ == "__main__":
    unittest.main()