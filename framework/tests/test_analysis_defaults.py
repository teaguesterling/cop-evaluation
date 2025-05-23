import unittest
import tempfile
import os
from cop_python.analysis.extractor import (
    extract_annotations_from_file, extract_annotations_from_directory,
    _apply_default_annotations, _infer_component_type, AnnotationInfo
)


class TestDefaultAnnotations(unittest.TestCase):
    """Test the default annotations functionality."""
    
    def setUp(self):
        """Set up test cases with sample code."""
        # Create temporary files for testing
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Sample code with some annotations
        self.sample_code = '''
@intent("Sample function")
def sample_function():
    """Sample function."""
    return True

@intent("Sample class")
class SampleClass:
    """Sample class."""
    
    @intent("Method with status")
    @implementation_status("IMPLEMENTED")
    def method_with_status(self):
        """Method with implementation status."""
        return True
    
    @intent("Method without status")
    def method_without_status(self):
        """Method without implementation status."""
        return False
'''
        
        self.file_path = os.path.join(self.temp_dir.name, "test_file.py")
        with open(self.file_path, 'w') as f:
            f.write(self.sample_code)
    
    def tearDown(self):
        """Clean up temporary files."""
        self.temp_dir.cleanup()
    
    def test_extract_without_defaults(self):
        """Test extracting annotations without defaults."""
        annotations = extract_annotations_from_file(self.file_path)
        
        # Should have 5 annotations: 4 intents + 1 implementation_status
        self.assertEqual(len(annotations), 5)
        
        # Group by component
        components = {}
        for anno in annotations:
            if anno.component_name not in components:
                components[anno.component_name] = set()
            components[anno.component_name].add(anno.annotation_type)
        
        # Check that some components don't have implementation_status
        self.assertNotIn("implementation_status", components["test_file.sample_function"])
        self.assertNotIn("implementation_status", components["test_file.SampleClass"])
        self.assertNotIn("implementation_status", components["test_file.SampleClass.method_without_status"])
        self.assertIn("implementation_status", components["test_file.SampleClass.method_with_status"])
    
    def test_extract_with_defaults(self):
        """Test extracting annotations with defaults."""
        default_annotations = {
            "implementation_status": "UNIMPLEMENTED",
            "risk": "low"
        }
        
        annotations = extract_annotations_from_file(
            self.file_path, 
            default_annotations=default_annotations
        )
        
        # Should have more annotations due to defaults
        self.assertGreater(len(annotations), 5)
        
        # Group by component and check for defaults
        components = {}
        defaults_added = []
        
        for anno in annotations:
            if anno.component_name not in components:
                components[anno.component_name] = {}
            components[anno.component_name][anno.annotation_type] = anno
            
            if anno.metadata.get("is_default", False):
                defaults_added.append((anno.component_name, anno.annotation_type))
        
        # All components should now have implementation_status
        for component_name in components:
            self.assertIn("implementation_status", components[component_name])
            self.assertIn("risk", components[component_name])
        
        # Check that defaults were added where expected
        expected_defaults = [
            ("test_file.sample_function", "implementation_status"),
            ("test_file.sample_function", "risk"),
            ("test_file.SampleClass", "implementation_status"), 
            ("test_file.SampleClass", "risk"),
            ("test_file.SampleClass.method_with_status", "risk"),
            ("test_file.SampleClass.method_without_status", "implementation_status"),
            ("test_file.SampleClass.method_without_status", "risk"),
        ]
        
        for expected in expected_defaults:
            self.assertIn(expected, defaults_added)
    
    def test_default_annotation_properties(self):
        """Test that default annotations have correct properties."""
        default_annotations = {"implementation_status": "UNIMPLEMENTED"}
        
        annotations = extract_annotations_from_file(
            self.file_path,
            default_annotations=default_annotations
        )
        
        # Find a default annotation
        default_anno = None
        for anno in annotations:
            if anno.metadata.get("is_default", False):
                default_anno = anno
                break
        
        self.assertIsNotNone(default_anno)
        self.assertEqual(default_anno.value, "UNIMPLEMENTED")
        self.assertEqual(default_anno.line_number, 0)
        self.assertTrue(default_anno.metadata["is_default"])
        self.assertIsNotNone(default_anno.component_info)  # Should inherit from first annotation
        self.assertIsNotNone(default_anno.metrics)  # Should inherit metrics
    
    def test_no_defaults_when_annotation_exists(self):
        """Test that defaults are not applied when annotation already exists."""
        default_annotations = {"implementation_status": "UNIMPLEMENTED"}
        
        annotations = extract_annotations_from_file(
            self.file_path,
            default_annotations=default_annotations
        )
        
        # Find method_with_status annotations
        method_annotations = [a for a in annotations 
                            if "method_with_status" in a.component_name 
                            and a.annotation_type == "implementation_status"]
        
        # Should only have one implementation_status annotation for this method
        self.assertEqual(len(method_annotations), 1)
        
        # And it should not be a default
        self.assertFalse(method_annotations[0].metadata.get("is_default", False))
        self.assertEqual(method_annotations[0].value, "IMPLEMENTED")


class TestApplyDefaultAnnotations(unittest.TestCase):
    """Test the _apply_default_annotations function directly."""
    
    def test_apply_defaults_to_empty_list(self):
        """Test applying defaults to an empty annotation list."""
        result = _apply_default_annotations([], {"risk": "low"}, "test.py")
        self.assertEqual(len(result), 0)
    
    def test_apply_defaults_basic(self):
        """Test basic default application."""
        # Create a sample annotation
        sample_annotation = AnnotationInfo(
            annotation_type="intent",
            component_name="test.component",
            component_type="function",
            file_path="test.py",
            line_number=5,
            value="Test intent",
            metadata={},
            component_info={"docstring": "Test"},
            start_line=4,
            end_line=6,
            actual_start_line=5,
            metrics={"complexity": 1}
        )
        
        defaults = {"implementation_status": "UNIMPLEMENTED"}
        result = _apply_default_annotations([sample_annotation], defaults, "test.py")
        
        # Should have 2 annotations now
        self.assertEqual(len(result), 2)
        
        # Find the default annotation
        default_anno = None
        for anno in result:
            if anno.metadata.get("is_default", False):
                default_anno = anno
                break
        
        self.assertIsNotNone(default_anno)
        self.assertEqual(default_anno.annotation_type, "implementation_status")
        self.assertEqual(default_anno.value, "UNIMPLEMENTED")
        self.assertEqual(default_anno.component_name, "test.component")
        self.assertEqual(default_anno.component_type, "function")
        self.assertTrue(default_anno.metadata["is_default"])
    
    def test_no_defaults_when_exists(self):
        """Test that defaults are not applied when annotation already exists."""
        # Create annotations for the same component
        existing_annotation = AnnotationInfo(
            annotation_type="implementation_status",
            component_name="test.component", 
            component_type="function",
            file_path="test.py",
            line_number=5,
            value="IMPLEMENTED",
            metadata={},
            component_info={"docstring": "Test"},
            start_line=4,
            end_line=6,
            actual_start_line=5,
            metrics={}
        )
        
        defaults = {"implementation_status": "UNIMPLEMENTED"}
        result = _apply_default_annotations([existing_annotation], defaults, "test.py")
        
        # Should still have only 1 annotation
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].value, "IMPLEMENTED")
        self.assertFalse(result[0].metadata.get("is_default", False))


class TestInferComponentType(unittest.TestCase):
    """Test the _infer_component_type function."""
    
    def test_infer_function(self):
        """Test inferring function type."""
        self.assertEqual(_infer_component_type("module.function"), "function")
    
    def test_infer_method(self):
        """Test inferring method type."""
        self.assertEqual(_infer_component_type("module.class.method"), "method")
    
    def test_infer_unknown(self):
        """Test inferring unknown type."""
        self.assertEqual(_infer_component_type("single_name"), "unknown")
    
    def test_infer_deeply_nested(self):
        """Test inferring deeply nested components."""
        self.assertEqual(_infer_component_type("package.module.class.method"), "method")


class TestDirectoryDefaults(unittest.TestCase):
    """Test default annotations with directory extraction."""
    
    def setUp(self):
        """Set up test directory with multiple files."""
        self.temp_dir = tempfile.TemporaryDirectory()
        
        # Create multiple files
        file1_content = '''
@intent("File 1 function")
def file1_function():
    return True
'''
        
        file2_content = '''
@intent("File 2 class")
@implementation_status("PARTIAL")
class File2Class:
    pass
'''
        
        file1_path = os.path.join(self.temp_dir.name, "file1.py")
        file2_path = os.path.join(self.temp_dir.name, "file2.py")
        
        with open(file1_path, 'w') as f:
            f.write(file1_content)
        with open(file2_path, 'w') as f:
            f.write(file2_content)
    
    def tearDown(self):
        """Clean up temporary files."""
        self.temp_dir.cleanup()
    
    def test_directory_defaults(self):
        """Test applying defaults to directory extraction."""
        defaults = {"implementation_status": "UNIMPLEMENTED"}
        
        annotations = extract_annotations_from_directory(
            self.temp_dir.name,
            default_annotations=defaults
        )
        
        # Should have annotations from both files plus defaults
        self.assertGreater(len(annotations), 2)
        
        # Check that file1_function got a default implementation_status
        file1_defaults = [a for a in annotations 
                         if "file1_function" in a.component_name 
                         and a.annotation_type == "implementation_status"
                         and a.metadata.get("is_default", False)]
        
        self.assertEqual(len(file1_defaults), 1)
        self.assertEqual(file1_defaults[0].value, "UNIMPLEMENTED")
        
        # Check that File2Class did NOT get a default (it already has one)
        file2_defaults = [a for a in annotations
                         if "File2Class" in a.component_name
                         and a.annotation_type == "implementation_status"
                         and a.metadata.get("is_default", False)]
        
        self.assertEqual(len(file2_defaults), 0)


if __name__ == "__main__":
    unittest.main()