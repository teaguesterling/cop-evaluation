import unittest
import os
import json
import tempfile
from cop_python.analysis.extractor import AnnotationInfo
from cop_python.analysis.graph import (
    NodeType, EdgeType, Node, ConceptNode, AnnotationNode, 
    Edge, RelationshipEdge, ConceptGraph
)


class TestNodeTypes(unittest.TestCase):
    """Test the node types Enum."""
    
    def test_node_types(self):
        """Test that node types are defined correctly."""
        self.assertEqual(NodeType.COMPONENT, "component")
        self.assertEqual(NodeType.ANNOTATION, "annotation")
        self.assertEqual(NodeType.TEST, "test")
        self.assertEqual(NodeType.DECISION, "decision")
        # Add other node types as needed


class TestEdgeTypes(unittest.TestCase):
    """Test the edge types Enum."""
    
    def test_edge_types(self):
        """Test that edge types are defined correctly."""
        self.assertEqual(EdgeType.HAS_ANNOTATION, "has_annotation")
        self.assertEqual(EdgeType.CALLS, "calls")
        self.assertEqual(EdgeType.DEPENDS_ON, "depends_on")
        # Add other edge types as needed


class TestNode(unittest.TestCase):
    """Test the Node class."""
    
    def test_node_creation(self):
        """Test creating a node."""
        node = Node("node1", NodeType.COMPONENT, {"key": "value"})
        self.assertEqual(node.id, "node1")
        self.assertEqual(node.node_type, NodeType.COMPONENT)
        self.assertEqual(node.properties, {"key": "value"})
    
    def test_node_to_dict(self):
        """Test converting a node to a dictionary."""
        node = Node("node1", NodeType.COMPONENT, {"key": "value"})
        node_dict = node.to_dict()
        self.assertEqual(node_dict["id"], "node1")
        self.assertEqual(node_dict["type"], NodeType.COMPONENT)
        self.assertEqual(node_dict["key"], "value")
    
    def test_node_from_dict(self):
        """Test creating a node from a dictionary."""
        node_dict = {
            "id": "node1",
            "type": NodeType.COMPONENT,
            "key": "value"
        }
        node = Node.from_dict(node_dict)
        self.assertEqual(node.id, "node1")
        self.assertEqual(node.node_type, NodeType.COMPONENT)
        self.assertEqual(node.properties, {"key": "value"})


class TestConceptNode(unittest.TestCase):
    """Test the ConceptNode class."""
    
    def test_concept_node_creation(self):
        """Test creating a concept node."""
        node = ConceptNode(
            id="component:test.component",
            component_type="function",
            file_path="test.py",
            name="test.component",
            component_info={"docstring": "Test doc"},
            start_line=10,
            end_line=15,
            actual_start_line=12
        )
        self.assertEqual(node.id, "component:test.component")
        self.assertEqual(node.component_type, "function")
        self.assertEqual(node.file_path, "test.py")
        self.assertEqual(node.name, "test.component")
        self.assertEqual(node.component_info, {"docstring": "Test doc"})
        self.assertEqual(node.start_line, 10)
        self.assertEqual(node.end_line, 15)
        self.assertEqual(node.actual_start_line, 12)
    
    def test_concept_node_properties(self):
        """Test that properties are set correctly."""
        node = ConceptNode(
            id="component:test.component",
            component_type="function",
            file_path="test.py",
            name="test.component",
            component_info={"docstring": "Test doc"},
            start_line=10,
            end_line=15,
            actual_start_line=12
        )
        self.assertEqual(node.properties["component_type"], "function")
        self.assertEqual(node.properties["file_path"], "test.py")
        self.assertEqual(node.properties["name"], "test.component")
        self.assertEqual(node.properties["component_info"], {"docstring": "Test doc"})
        self.assertEqual(node.properties["start_line"], 10)
        self.assertEqual(node.properties["end_line"], 15)
        self.assertEqual(node.properties["actual_start_line"], 12)


class TestAnnotationNode(unittest.TestCase):
    """Test the AnnotationNode class."""
    
    def test_annotation_node_creation(self):
        """Test creating an annotation node."""
        node = AnnotationNode(
            id="annotation:intent:test.component:12345",
            annotation_type="intent",
            value="Test intent",
            metadata={"key": "value"}
        )
        self.assertEqual(node.id, "annotation:intent:test.component:12345")
        self.assertEqual(node.annotation_type, "intent")
        self.assertEqual(node.value, "Test intent")
        self.assertEqual(node.metadata, {"key": "value"})
    
    def test_annotation_node_properties(self):
        """Test that properties are set correctly."""
        node = AnnotationNode(
            id="annotation:intent:test.component:12345",
            annotation_type="intent",
            value="Test intent",
            metadata={"key": "value"}
        )
        self.assertEqual(node.properties["annotation_type"], "intent")
        self.assertEqual(node.properties["value"], "Test intent")
        self.assertEqual(node.properties["metadata"], {"key": "value"})


class TestEdge(unittest.TestCase):
    """Test the Edge class."""
    
    def test_edge_creation(self):
        """Test creating an edge."""
        edge = Edge("source1", "target1", EdgeType.HAS_ANNOTATION, {"key": "value"})
        self.assertEqual(edge.source_id, "source1")
        self.assertEqual(edge.target_id, "target1")
        self.assertEqual(edge.edge_type, EdgeType.HAS_ANNOTATION)
        self.assertEqual(edge.properties, {"key": "value"})
    
    def test_edge_to_dict(self):
        """Test converting an edge to a dictionary."""
        edge = Edge("source1", "target1", EdgeType.HAS_ANNOTATION, {"key": "value"})
        edge_dict = edge.to_dict()
        self.assertEqual(edge_dict["source"], "source1")
        self.assertEqual(edge_dict["target"], "target1")
        self.assertEqual(edge_dict["type"], EdgeType.HAS_ANNOTATION)
        self.assertEqual(edge_dict["key"], "value")
    
    def test_edge_from_dict(self):
        """Test creating an edge from a dictionary."""
        edge_dict = {
            "source": "source1",
            "target": "target1",
            "type": EdgeType.HAS_ANNOTATION,
            "key": "value"
        }
        edge = Edge.from_dict(edge_dict)
        self.assertEqual(edge.source_id, "source1")
        self.assertEqual(edge.target_id, "target1")
        self.assertEqual(edge.edge_type, EdgeType.HAS_ANNOTATION)
        self.assertEqual(edge.properties, {"key": "value"})


class TestRelationshipEdge(unittest.TestCase):
    """Test the RelationshipEdge class."""
    
    def test_relationship_edge_creation(self):
        """Test creating a relationship edge."""
        edge = RelationshipEdge(
            source_id="source1",
            target_id="target1",
            edge_type=EdgeType.HAS_ANNOTATION,
            weight=0.5
        )
        self.assertEqual(edge.source_id, "source1")
        self.assertEqual(edge.target_id, "target1")
        self.assertEqual(edge.edge_type, EdgeType.HAS_ANNOTATION)
        self.assertEqual(edge.weight, 0.5)
        self.assertEqual(edge.properties["weight"], 0.5)


class TestConceptGraph(unittest.TestCase):
    """Test the ConceptGraph class."""
    
    def setUp(self):
        """Set up test cases with sample annotations."""
        self.annotations = [
            AnnotationInfo(
                annotation_type="intent",
                component_name="test.component1",
                component_type="function",
                file_path="test.py",
                line_number=10,
                value="Test intent 1",
                metadata={},
                component_info={"docstring": "Test doc 1"},
                start_line=8,
                end_line=12,
                actual_start_line=10
            ),
            AnnotationInfo(
                annotation_type="implementation_status",
                component_name="test.component1",
                component_type="function",
                file_path="test.py",
                line_number=11,
                value="IMPLEMENTED",
                metadata={},
                component_info={"docstring": "Test doc 1"},
                start_line=8,
                end_line=12,
                actual_start_line=10
            ),
            AnnotationInfo(
                annotation_type="intent",
                component_name="test.component2",
                component_type="class",
                file_path="test.py",
                line_number=15,
                value="Test intent 2",
                metadata={},
                component_info={"docstring": "Test doc 2"},
                start_line=14,
                end_line=20,
                actual_start_line=15
            )
        ]
        
        # Create a temp file for graph export/import
        self.temp_dir = tempfile.TemporaryDirectory()
        self.export_file = os.path.join(self.temp_dir.name, "graph.json")
    
    def tearDown(self):
        """Clean up temporary files."""
        self.temp_dir.cleanup()
    
    def test_add_node(self):
        """Test adding a node to the graph."""
        graph = ConceptGraph()
        node = Node("node1", NodeType.COMPONENT)
        graph.add_node(node)
        self.assertEqual(len(graph.nodes), 1)
        self.assertIn("node1", graph.nodes)
    
    def test_add_edge(self):
        """Test adding an edge to the graph."""
        graph = ConceptGraph()
        edge = Edge("source1", "target1", EdgeType.HAS_ANNOTATION)
        graph.add_edge(edge)
        self.assertEqual(len(graph.edges), 1)
        self.assertEqual(graph.edges[0].source_id, "source1")
    
    def test_get_node(self):
        """Test getting a node by ID."""
        graph = ConceptGraph()
        node = Node("node1", NodeType.COMPONENT)
        graph.add_node(node)
        retrieved = graph.get_node("node1")
        self.assertEqual(retrieved.id, "node1")
    
    def test_get_edges(self):
        """Test getting edges by criteria."""
        graph = ConceptGraph()
        
        edge1 = Edge("source1", "target1", EdgeType.HAS_ANNOTATION)
        edge2 = Edge("source1", "target2", EdgeType.CALLS)
        edge3 = Edge("source2", "target1", EdgeType.HAS_ANNOTATION)
        
        graph.add_edge(edge1)
        graph.add_edge(edge2)
        graph.add_edge(edge3)
        
        # Get by source
        source_edges = graph.get_edges(source_id="source1")
        self.assertEqual(len(source_edges), 2)
        
        # Get by target
        target_edges = graph.get_edges(target_id="target1")
        self.assertEqual(len(target_edges), 2)
        
        # Get by type
        type_edges = graph.get_edges(edge_type=EdgeType.HAS_ANNOTATION)
        self.assertEqual(len(type_edges), 2)
        
        # Get by combination
        combined_edges = graph.get_edges(
            source_id="source1", 
            edge_type=EdgeType.HAS_ANNOTATION
        )
        self.assertEqual(len(combined_edges), 1)
    
    def test_build_from_annotations(self):
        """Test building a graph from annotations."""
        graph = ConceptGraph()
        graph.build_from_annotations(self.annotations)
        
        # Should have 2 component nodes and 3 annotation nodes
        component_nodes = [n for n in graph.nodes.values() 
                          if n.node_type == NodeType.COMPONENT]
        annotation_nodes = [n for n in graph.nodes.values() 
                           if n.node_type == NodeType.ANNOTATION]
        
        self.assertEqual(len(component_nodes), 2)
        self.assertEqual(len(annotation_nodes), 3)
        
        # Should have 3 HAS_ANNOTATION edges
        edges = graph.get_edges(edge_type=EdgeType.HAS_ANNOTATION)
        self.assertEqual(len(edges), 3)
    
    def test_query_components(self):
        """Test querying components based on criteria."""
        graph = ConceptGraph()
        graph.build_from_annotations(self.annotations)
        
        # Query by component type
        class_components = graph.query_components(component_type="class")
        self.assertEqual(len(class_components), 1)
        self.assertEqual(class_components[0].properties["name"], "test.component2")
        
        # Query by annotation type
        implemented_components = graph.query_components(
            annotation_type="implementation_status", 
            annotation_value="IMPLEMENTED"
        )
        self.assertEqual(len(implemented_components), 1)
        self.assertEqual(implemented_components[0].properties["name"], "test.component1")
    
    def test_query_annotations(self):
        """Test querying annotations based on criteria."""
        graph = ConceptGraph()
        graph.build_from_annotations(self.annotations)
        
        # Get all annotations
        all_annotations = graph.query_annotations()
        self.assertEqual(len(all_annotations), 3)
        
        # Query by annotation type
        intent_annotations = graph.query_annotations(annotation_type="intent")
        self.assertEqual(len(intent_annotations), 2)
        
        # Query by component
        component1_id = f"component:test.component1"
        component1_annotations = graph.query_annotations(component_id=component1_id)
        self.assertEqual(len(component1_annotations), 2)
    
    def test_export_import_json(self):
        """Test exporting and importing a graph to/from JSON."""
        # Create and populate a graph
        graph = ConceptGraph()
        graph.build_from_annotations(self.annotations)
        
        # Export to JSON
        graph.export_to_json(self.export_file)
        self.assertTrue(os.path.exists(self.export_file))
        
        # Import from JSON
        imported_graph = ConceptGraph.import_from_json(self.export_file)
        
        # Verify node count
        self.assertEqual(len(imported_graph.nodes), len(graph.nodes))
        
        # Verify edge count
        self.assertEqual(len(imported_graph.edges), len(graph.edges))


if __name__ == "__main__":
    unittest.main()