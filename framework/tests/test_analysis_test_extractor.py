"""
Tests for the test relationship extraction functionality.
"""

import ast
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from cop_python.analysis.test_extractor import (
    TestRelationship,
    TestRelationshipExtractor,
    extract_test_relationships_from_file,
    extract_test_relationships_from_directory,
)


class TestTestRelationship:
    """Test the TestRelationship NamedTuple."""
    
    def test_test_relationship_creation(self):
        """Test creating a TestRelationship object."""
        rel = TestRelationship(
            test_name="test_module.test_function",
            test_type="unit",
            target_component="MyClass.method",
            annotation_ref={"type": "invariant", "value": "x > 0"},
            file_path="/path/to/test.py",
            line_number=10,
            test_info={"docstring": "Test method"},
            start_line=8,
            end_line=15,
            actual_start_line=10,
            metrics={"complexity": 1}
        )
        
        assert rel.test_name == "test_module.test_function"
        assert rel.test_type == "unit"
        assert rel.target_component == "MyClass.method"
        assert rel.annotation_ref == {"type": "invariant", "value": "x > 0"}
        assert rel.file_path == "/path/to/test.py"
        assert rel.line_number == 10
        assert rel.test_info == {"docstring": "Test method"}
        assert rel.start_line == 8
        assert rel.end_line == 15
        assert rel.actual_start_line == 10
        assert rel.metrics == {"complexity": 1}


class TestTestRelationshipExtractor:
    """Test the TestRelationshipExtractor class."""
    
    def test_init(self):
        """Test extractor initialization."""
        extractor = TestRelationshipExtractor("/path/to/test.py", "# test code")
        assert extractor.file_path == "/path/to/test.py"
        assert extractor.source_code == "# test code"
        assert extractor.relationships == []
        assert extractor.current_class is None
        assert extractor.metrics_providers is not None
    
    def test_get_module_name(self):
        """Test module name extraction."""
        extractor = TestRelationshipExtractor("/path/to/test.py", "")
        
        # Test fallback to filename
        module_name = extractor._get_module_name("/some/path/test_module.py")
        assert module_name == "test_module"
    
    def test_get_test_name_function(self):
        """Test test name generation for functions."""
        extractor = TestRelationshipExtractor("test_module.py", "")
        extractor.module_name = "test_module"
        
        node = Mock()
        node.name = "test_something"
        
        name = extractor._get_test_name(node)
        assert name == "test_module.test_something"
    
    def test_get_test_name_method(self):
        """Test test name generation for class methods."""
        extractor = TestRelationshipExtractor("test_module.py", "")
        extractor.module_name = "test_module"
        extractor.current_class = "TestClass"
        
        node = Mock()
        node.name = "test_method"
        
        name = extractor._get_test_name(node)
        assert name == "test_module.TestClass.test_method"
    
    def test_extract_test_info_simple(self):
        """Test extracting test info from a simple function."""
        source = '''
def test_function():
    """Test docstring."""
    pass
'''
        tree = ast.parse(source)
        func_node = tree.body[0]
        
        extractor = TestRelationshipExtractor("test.py", source)
        info = extractor._extract_test_info(func_node)
        
        assert info["docstring"] == "Test docstring."
        assert info["params"] == []
        assert "returns" not in info
    
    def test_extract_test_info_with_params(self):
        """Test extracting test info from a function with parameters."""
        source = '''
def test_function(self, param: str) -> None:
    """Test with parameters."""
    pass
'''
        tree = ast.parse(source)
        func_node = tree.body[0]
        
        extractor = TestRelationshipExtractor("test.py", source)
        info = extractor._extract_test_info(func_node)
        
        assert info["docstring"] == "Test with parameters."
        assert len(info["params"]) == 2
        assert info["params"][0]["name"] == "self"
        assert info["params"][1]["name"] == "param"
        assert info["params"][1]["annotation"] == "str"
        assert info["returns"] == "None"
    
    def test_format_annotation_simple(self):
        """Test formatting simple annotations."""
        source = "def func(x: int): pass"
        tree = ast.parse(source)
        func_node = tree.body[0]
        annotation = func_node.args.args[0].annotation
        
        extractor = TestRelationshipExtractor("test.py", "")
        formatted = extractor._format_annotation(annotation)
        assert formatted == "int"
    
    def test_format_annotation_complex(self):
        """Test formatting complex annotations."""
        source = "def func(x: List[Dict[str, int]]): pass"
        tree = ast.parse(source)
        func_node = tree.body[0]
        annotation = func_node.args.args[0].annotation
        
        extractor = TestRelationshipExtractor("test.py", "")
        formatted = extractor._format_annotation(annotation)
        assert "List" in formatted
        assert "Dict" in formatted
    
    def test_extract_test_relationships_simple_decorator(self):
        """Test extracting relationships from simple test decorators."""
        source = '''
@test_for("MyClass.method")
def test_something():
    pass
'''
        tree = ast.parse(source)
        func_node = tree.body[0]
        
        extractor = TestRelationshipExtractor("test.py", source)
        relationships = extractor._extract_test_relationships(func_node)
        
        assert len(relationships) == 1
        rel = relationships[0]
        assert rel["target_component"] == "MyClass.method"
        assert rel["test_type"] == "unit"
        assert rel["annotation_ref"] is None
    
    def test_extract_test_relationships_with_annotation(self):
        """Test extracting relationships with annotation references."""
        source = '''
@test_invariant("MyClass.method", "x > 0")
def test_invariant():
    pass
'''
        tree = ast.parse(source)
        func_node = tree.body[0]
        
        extractor = TestRelationshipExtractor("test.py", source)
        relationships = extractor._extract_test_relationships(func_node)
        
        assert len(relationships) == 1
        rel = relationships[0]
        assert rel["target_component"] == "MyClass.method"
        assert rel["annotation_ref"]["type"] == "invariant"
        assert rel["annotation_ref"]["value"] == "x > 0"
    
    def test_extract_test_relationships_test_for_with_annotation(self):
        """Test extracting relationships from @test_for with annotation keywords."""
        source = '''
@test_for("MyClass.method", invariant="x > 0")
def test_invariant():
    pass
'''
        tree = ast.parse(source)
        func_node = tree.body[0]
        
        extractor = TestRelationshipExtractor("test.py", source)
        relationships = extractor._extract_test_relationships(func_node)
        
        assert len(relationships) == 1
        rel = relationships[0]
        assert rel["target_component"] == "MyClass.method"
        assert rel["annotation_ref"]["type"] == "invariant"
        assert rel["annotation_ref"]["value"] == "x > 0"
    
    def test_extract_arg_value_various_types(self):
        """Test extracting argument values from different AST node types."""
        extractor = TestRelationshipExtractor("test.py", "")
        
        # String constant
        node = ast.Constant(value="test_string")
        assert extractor._extract_arg_value(node) == "test_string"
        
        # Integer constant
        node = ast.Constant(value=42)
        assert extractor._extract_arg_value(node) == "42"
        
        # Variable name
        node = ast.Name(id="variable_name", ctx=ast.Load())
        assert extractor._extract_arg_value(node) == "<variable:variable_name>"
    
    def test_visit_function_with_test_decorators(self):
        """Test visiting a function with test decorators."""
        source = '''
@test_for("MyClass.method")
def test_something():
    """Test something."""
    pass
'''
        tree = ast.parse(source)
        
        extractor = TestRelationshipExtractor("test_module.py", source)
        extractor.module_name = "test_module"
        extractor.visit(tree)
        
        assert len(extractor.relationships) == 1
        rel = extractor.relationships[0]
        assert rel.test_name == "test_module.test_something"
        assert rel.target_component == "MyClass.method"
        assert rel.test_info["docstring"] == "Test something."
    
    def test_visit_class_with_test_methods(self):
        """Test visiting a class with test methods."""
        source = '''
class TestMyClass:
    @test_for("MyClass.method")
    def test_method(self):
        """Test method."""
        pass
'''
        tree = ast.parse(source)
        
        extractor = TestRelationshipExtractor("test_module.py", source)
        extractor.module_name = "test_module"
        extractor.visit(tree)
        
        assert len(extractor.relationships) == 1
        rel = extractor.relationships[0]
        assert rel.test_name == "test_module.TestMyClass.test_method"
    
    def test_multiple_test_decorators(self):
        """Test function with multiple test decorators."""
        source = '''
@test_invariant("MyClass.method", "x > 0")
@test_risk("MyClass.method", "HIGH")
def test_multiple():
    pass
'''
        tree = ast.parse(source)
        
        extractor = TestRelationshipExtractor("test_module.py", source)
        extractor.module_name = "test_module"
        extractor.visit(tree)
        
        assert len(extractor.relationships) == 2
        
        # Check invariant test
        invariant_rel = next(r for r in extractor.relationships 
                           if r.annotation_ref and r.annotation_ref["type"] == "invariant")
        assert invariant_rel.annotation_ref["value"] == "x > 0"
        
        # Check risk test
        risk_rel = next(r for r in extractor.relationships 
                       if r.annotation_ref and r.annotation_ref["type"] == "risk")
        assert risk_rel.annotation_ref["value"] == "HIGH"


class TestTestRelationshipFunctions:
    """Test the module-level functions."""
    
    def test_extract_test_relationships_from_file(self):
        """Test extracting test relationships from a file."""
        test_code = '''
@test_for("MyClass.method")
def test_something():
    """Test something."""
    pass

@test_invariant("AnotherClass.other_method", "y < 10")
def test_invariant():
    """Test invariant."""
    pass
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            f.flush()
            
            try:
                relationships = extract_test_relationships_from_file(f.name)
                
                assert len(relationships) == 2
                
                # Check first relationship
                rel1 = next(r for r in relationships if "test_something" in r.test_name)
                assert rel1.target_component == "MyClass.method"
                assert rel1.annotation_ref is None
                
                # Check second relationship
                rel2 = next(r for r in relationships if "test_invariant" in r.test_name)
                assert rel2.target_component == "AnotherClass.other_method"
                assert rel2.annotation_ref["type"] == "invariant"
                assert rel2.annotation_ref["value"] == "y < 10"
                
            finally:
                os.unlink(f.name)
    
    def test_extract_test_relationships_from_file_syntax_error(self):
        """Test handling files with syntax errors."""
        bad_code = '''
def test_something(
    # Syntax error - missing closing parenthesis
    pass
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(bad_code)
            f.flush()
            
            try:
                relationships = extract_test_relationships_from_file(f.name)
                assert relationships == []
                
            finally:
                os.unlink(f.name)
    
    def test_extract_test_relationships_from_directory(self):
        """Test extracting test relationships from a directory."""
        # Create temporary directory with test files
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test file 1
            test_file1 = temp_path / "test_module1.py"
            test_file1.write_text('''
@test_for("Module1.function")
def test_function():
    pass
''')
            
            # Create test file 2 in subdirectory
            subdir = temp_path / "subpackage"
            subdir.mkdir()
            test_file2 = subdir / "test_module2.py"
            test_file2.write_text('''
@test_invariant("Module2.method", "x > 0")
def test_method():
    pass
''')
            
            # Create non-test file (should be ignored)
            regular_file = temp_path / "regular.py"
            regular_file.write_text('''
def regular_function():
    pass
''')
            
            # Extract relationships
            relationships = extract_test_relationships_from_directory(str(temp_path))
            
            assert len(relationships) == 2
            
            # Check that both test files were processed
            file_paths = {rel.file_path for rel in relationships}
            assert str(test_file1) in file_paths
            assert str(test_file2) in file_paths
            assert str(regular_file) not in file_paths
    
    def test_extract_test_relationships_from_directory_non_recursive(self):
        """Test extracting test relationships from directory without recursion."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Create test file in root
            test_file1 = temp_path / "test_root.py"
            test_file1.write_text('''
@test_for("Root.function")
def test_function():
    pass
''')
            
            # Create test file in subdirectory
            subdir = temp_path / "subpackage"
            subdir.mkdir()
            test_file2 = subdir / "test_sub.py"
            test_file2.write_text('''
@test_for("Sub.function")
def test_function():
    pass
''')
            
            # Extract relationships non-recursively
            relationships = extract_test_relationships_from_directory(
                str(temp_path), recursive=False
            )
            
            # Should only find the root test file
            assert len(relationships) == 1
            assert str(test_file1) in relationships[0].file_path
    
    @patch('cop_python.analysis.test_extractor.get_default_metrics_providers')
    def test_extract_with_custom_metrics_providers(self, mock_get_providers):
        """Test extraction with custom metrics providers."""
        # Mock metrics provider
        mock_provider = Mock()
        mock_provider.calculate_metrics.return_value = {"test_metric": 42}
        mock_get_providers.return_value = [mock_provider]
        
        test_code = '''
@test_for("MyClass.method")
def test_something():
    pass
'''
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(test_code)
            f.flush()
            
            try:
                relationships = extract_test_relationships_from_file(f.name, [mock_provider])
                
                assert len(relationships) == 1
                assert relationships[0].metrics["test_metric"] == 42
                mock_provider.calculate_metrics.assert_called_once()
                
            finally:
                os.unlink(f.name)


class TestGraphIntegration:
    """Test integration of test relationships with the concept graph."""
    
    def test_test_node_creation(self):
        """Test creating TestNode objects."""
        from cop_python.analysis.graph import TestNode, NodeType
        
        test_node = TestNode(
            id="test:test_module.test_function",
            test_name="test_module.test_function",
            test_type="unit",
            file_path="/path/to/test.py",
            line_number=10,
            test_info={"docstring": "Test function"},
            start_line=8,
            end_line=15,
            actual_start_line=10,
            metrics={"complexity": 1}
        )
        
        assert test_node.id == "test:test_module.test_function"
        assert test_node.node_type == NodeType.TEST
        assert test_node.test_name == "test_module.test_function"
        assert test_node.test_type == "unit"
        assert test_node.file_path == "/path/to/test.py"
        assert test_node.line_number == 10
        assert test_node.test_info == {"docstring": "Test function"}
        assert test_node.properties["start_line"] == 8
        assert test_node.properties["end_line"] == 15
        assert test_node.properties["actual_start_line"] == 10
        assert test_node.properties["metrics"] == {"complexity": 1}
    
    def test_add_test_relationship_to_graph(self):
        """Test adding test relationships to the concept graph."""
        from cop_python.analysis.graph import ConceptGraph, EdgeType
        from cop_python.analysis.test_extractor import TestRelationship
        
        graph = ConceptGraph()
        
        # Create a test relationship
        test_rel = TestRelationship(
            test_name="test_module.test_function",
            test_type="unit",
            target_component="MyClass.method",
            annotation_ref={"type": "invariant", "value": "x > 0"},
            file_path="/path/to/test.py",
            line_number=10,
            test_info={"docstring": "Test function"},
            start_line=8,
            end_line=15,
            actual_start_line=10,
            metrics={"complexity": 1}
        )
        
        # Add to graph
        graph.add_test_relationship(test_rel)
        
        # Verify test node was created
        test_node = graph.get_node("test:test_module.test_function")
        assert test_node is not None
        assert test_node.test_name == "test_module.test_function"
        
        # Verify verification edges were created
        component_edges = graph.get_edges(
            source_id="component:MyClass.method",
            edge_type=EdgeType.VERIFIED_BY
        )
        assert len(component_edges) == 1
        assert component_edges[0].target_id == "test:test_module.test_function"
        
        annotation_edges = graph.get_edges(
            source_id="annotation:MyClass.method:invariant",
            edge_type=EdgeType.VERIFIED_BY
        )
        assert len(annotation_edges) == 1
        assert annotation_edges[0].target_id == "test:test_module.test_function"
    
    def test_build_from_test_relationships(self):
        """Test building graph from multiple test relationships."""
        from cop_python.analysis.graph import ConceptGraph
        from cop_python.analysis.test_extractor import TestRelationship
        
        graph = ConceptGraph()
        
        # Create multiple test relationships
        test_rels = [
            TestRelationship(
                test_name="test_module.test_function1",
                test_type="unit",
                target_component="MyClass.method1",
                annotation_ref=None,
                file_path="/path/to/test.py",
                line_number=10,
                test_info={},
                start_line=8,
                end_line=15,
                actual_start_line=10,
                metrics={}
            ),
            TestRelationship(
                test_name="test_module.test_function2",
                test_type="integration",
                target_component="MyClass.method1",
                annotation_ref={"type": "risk", "value": "HIGH"},
                file_path="/path/to/test.py",
                line_number=20,
                test_info={},
                start_line=18,
                end_line=25,
                actual_start_line=20,
                metrics={}
            )
        ]
        
        # Build graph from relationships
        graph.build_from_test_relationships(test_rels)
        
        # Verify both test nodes were created
        assert graph.get_node("test:test_module.test_function1") is not None
        assert graph.get_node("test:test_module.test_function2") is not None
        
        # Verify verification edges
        tests = graph.get_tests_for_component("component:MyClass.method1")
        assert len(tests) == 2
        
        test_names = {test.test_name for test in tests}
        assert "test_module.test_function1" in test_names
        assert "test_module.test_function2" in test_names
    
    def test_get_tests_for_component(self):
        """Test getting tests for a specific component."""
        from cop_python.analysis.graph import ConceptGraph
        from cop_python.analysis.test_extractor import TestRelationship
        
        graph = ConceptGraph()
        
        # Add test relationship
        test_rel = TestRelationship(
            test_name="test_module.test_function",
            test_type="unit",
            target_component="MyClass.method",
            annotation_ref=None,
            file_path="/path/to/test.py",
            line_number=10,
            test_info={},
            start_line=8,
            end_line=15,
            actual_start_line=10,
            metrics={}
        )
        graph.add_test_relationship(test_rel)
        
        # Get tests for component
        tests = graph.get_tests_for_component("component:MyClass.method")
        assert len(tests) == 1
        assert tests[0].test_name == "test_module.test_function"
        
        # No tests for different component
        no_tests = graph.get_tests_for_component("component:OtherClass.method")
        assert len(no_tests) == 0
    
    def test_get_tests_for_annotation(self):
        """Test getting tests for a specific annotation."""
        from cop_python.analysis.graph import ConceptGraph
        from cop_python.analysis.test_extractor import TestRelationship
        
        graph = ConceptGraph()
        
        # Add test relationship with annotation reference
        test_rel = TestRelationship(
            test_name="test_module.test_invariant",
            test_type="unit",
            target_component="MyClass.method",
            annotation_ref={"type": "invariant", "value": "x > 0"},
            file_path="/path/to/test.py",
            line_number=10,
            test_info={},
            start_line=8,
            end_line=15,
            actual_start_line=10,
            metrics={}
        )
        graph.add_test_relationship(test_rel)
        
        # Get tests for specific annotation
        tests = graph.get_tests_for_annotation("MyClass.method", "invariant")
        assert len(tests) == 1
        assert tests[0].test_name == "test_module.test_invariant"
        
        # No tests for different annotation type
        no_tests = graph.get_tests_for_annotation("MyClass.method", "risk")
        assert len(no_tests) == 0
    
    def test_get_verification_status(self):
        """Test getting verification status for a component."""
        from cop_python.analysis.graph import ConceptGraph
        from cop_python.analysis.test_extractor import TestRelationship
        
        graph = ConceptGraph()
        
        # Add multiple test relationships
        test_rels = [
            TestRelationship(
                test_name="test_module.test_unit",
                test_type="unit",
                target_component="MyClass.method",
                annotation_ref={"type": "invariant", "value": "x > 0"},
                file_path="/path/to/test.py",
                line_number=10,
                test_info={},
                start_line=8,
                end_line=15,
                actual_start_line=10,
                metrics={}
            ),
            TestRelationship(
                test_name="test_module.test_integration",
                test_type="integration",
                target_component="MyClass.method",
                annotation_ref={"type": "risk", "value": "HIGH"},
                file_path="/path/to/test.py",
                line_number=20,
                test_info={},
                start_line=18,
                end_line=25,
                actual_start_line=20,
                metrics={}
            ),
            TestRelationship(
                test_name="test_module.test_unit2",
                test_type="unit",
                target_component="MyClass.method",
                annotation_ref=None,
                file_path="/path/to/test.py",
                line_number=30,
                test_info={},
                start_line=28,
                end_line=35,
                actual_start_line=30,
                metrics={}
            )
        ]
        
        for rel in test_rels:
            graph.add_test_relationship(rel)
        
        # Get verification status
        status = graph.get_verification_status("component:MyClass.method")
        
        assert status["total_tests"] == 3
        assert status["has_tests"] is True
        assert status["test_types"]["unit"] == 2
        assert status["test_types"]["integration"] == 1
        assert status["annotation_coverage"]["invariant"] == 1
        assert status["annotation_coverage"]["risk"] == 1


if __name__ == "__main__":
    pytest.main([__file__])