import unittest
import os
import json
import tempfile
from cop_python.analysis.extractor import AnnotationInfo
from cop_python.analysis.graph import (
    ConceptGraph, NodeType, EdgeType, Node, ConceptNode, AnnotationNode, Edge
)
from cop_python.analysis.exporter import JSONLExporter


class TestJSONLExporter(unittest.TestCase):
    """Test the JSONLExporter class."""
    
    def setUp(self):
        """Set up test cases with a sample graph."""
        # Create a temporary directory for output
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = self.temp_dir.name

        # Create a sample graph
        self.graph = ConceptGraph()
        
        # Add component nodes
        component1 = ConceptNode(
            id="component:test.component1",
            component_type="function",
            file_path="test.py",
            name="test.component1",
            component_info={"docstring": "Test doc 1"},
            start_line=10,
            end_line=15,
            actual_start_line=12
        )
        
        component2 = ConceptNode(
            id="component:test.component2",
            component_type="class",
            file_path="test.py",
            name="test.component2",
            component_info={"docstring": "Test doc 2", "methods": ["method1", "method2"]},
            start_line=20,
            end_line=30,
            actual_start_line=22
        )
        
        self.graph.add_node(component1)
        self.graph.add_node(component2)
        
        # Add annotation nodes
        annotation1 = AnnotationNode(
            id="annotation:intent:test.component1:12345",
            annotation_type="intent",
            value="Test intent 1",
            metadata={}
        )
        
        annotation2 = AnnotationNode(
            id="annotation:implementation_status:test.component1:67890",
            annotation_type="implementation_status",
            value="IMPLEMENTED",
            metadata={}
        )
        
        annotation3 = AnnotationNode(
            id="annotation:intent:test.component2:54321",
            annotation_type="intent",
            value="Test intent 2",
            metadata={}
        )
        
        self.graph.add_node(annotation1)
        self.graph.add_node(annotation2)
        self.graph.add_node(annotation3)
        
        # Add edges
        edge1 = Edge(
            source_id="component:test.component1",
            target_id="annotation:intent:test.component1:12345",
            edge_type=EdgeType.HAS_ANNOTATION
        )
        
        edge2 = Edge(
            source_id="component:test.component1",
            target_id="annotation:implementation_status:test.component1:67890",
            edge_type=EdgeType.HAS_ANNOTATION
        )
        
        edge3 = Edge(
            source_id="component:test.component2",
            target_id="annotation:intent:test.component2:54321",
            edge_type=EdgeType.HAS_ANNOTATION
        )
        
        self.graph.add_edge(edge1)
        self.graph.add_edge(edge2)
        self.graph.add_edge(edge3)
    
    def tearDown(self):
        """Clean up temporary files."""
        self.temp_dir.cleanup()
    
    def test_export_graph(self):
        """Test exporting a graph to JSONL files."""
        exporter = JSONLExporter(self.output_dir)
        counts = exporter.export_graph(self.graph)
        
        # Verify counts
        self.assertEqual(counts["nodes"][NodeType.COMPONENT], 2)
        self.assertEqual(counts["nodes"][NodeType.ANNOTATION], 3)
        self.assertEqual(counts["edges"][EdgeType.HAS_ANNOTATION], 3)
        
        # Check that files were created
        component_file = os.path.join(self.output_dir, f"{NodeType.COMPONENT}.jsonl")
        annotation_file = os.path.join(self.output_dir, f"{NodeType.ANNOTATION}.jsonl")
        edge_file = os.path.join(self.output_dir, f"{EdgeType.HAS_ANNOTATION}.jsonl")
        metadata_file = os.path.join(self.output_dir, "metadata.json")
        
        self.assertTrue(os.path.exists(component_file))
        self.assertTrue(os.path.exists(annotation_file))
        self.assertTrue(os.path.exists(edge_file))
        self.assertTrue(os.path.exists(metadata_file))
        
        # Check metadata file
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
            self.assertEqual(metadata["total_nodes"], 5)
            self.assertEqual(metadata["total_edges"], 3)
    
    def test_exported_component_format(self):
        """Test that exported component nodes have the correct format."""
        exporter = JSONLExporter(self.output_dir)
        exporter.export_graph(self.graph)
        
        component_file = os.path.join(self.output_dir, f"{NodeType.COMPONENT}.jsonl")
        
        # Read component file
        with open(component_file, 'r') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 2)  # Should have 2 components
            
            # Parse the first component
            component = json.loads(lines[0])
            self.assertIn("id", component)
            self.assertIn("type", component)
            self.assertEqual(component["type"], NodeType.COMPONENT)
            self.assertIn("component_info", component)
            self.assertIn("start_line", component)
            self.assertIn("end_line", component)
            self.assertIn("actual_start_line", component)
    
    def test_exported_annotation_format(self):
        """Test that exported annotation nodes have the correct format."""
        exporter = JSONLExporter(self.output_dir)
        exporter.export_graph(self.graph)
        
        annotation_file = os.path.join(self.output_dir, f"{NodeType.ANNOTATION}.jsonl")
        
        # Read annotation file
        with open(annotation_file, 'r') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 3)  # Should have 3 annotations
            
            # Parse the first annotation
            annotation = json.loads(lines[0])
            self.assertIn("id", annotation)
            self.assertIn("type", annotation)
            self.assertEqual(annotation["type"], NodeType.ANNOTATION)
            self.assertIn("annotation_type", annotation)
            self.assertIn("value", annotation)
            self.assertIn("metadata", annotation)
    
    def test_exported_edge_format(self):
        """Test that exported edges have the correct format."""
        exporter = JSONLExporter(self.output_dir)
        exporter.export_graph(self.graph)
        
        edge_file = os.path.join(self.output_dir, f"{EdgeType.HAS_ANNOTATION}.jsonl")
        
        # Read edge file
        with open(edge_file, 'r') as f:
            lines = f.readlines()
            self.assertEqual(len(lines), 3)  # Should have 3 edges
            
            # Parse the first edge
            edge = json.loads(lines[0])
            self.assertIn("source", edge)
            self.assertIn("target", edge)
            self.assertIn("type", edge)
            self.assertEqual(edge["type"], EdgeType.HAS_ANNOTATION)


if __name__ == "__main__":
    unittest.main()