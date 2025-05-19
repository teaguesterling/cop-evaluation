"""
Concept graph representation for the COP framework.

This module provides classes for building, storing, and querying
the concept graph based on extracted COP annotations.
"""

import json
import os
import sqlite3
from typing import Dict, List, Any, Optional, Union, Set, Tuple, NamedTuple
from enum import Enum
from pathlib import Path
from datetime import datetime
from collections import defaultdict

from .extractor import AnnotationInfo


class NodeType(str, Enum):
    """Types of nodes in the concept graph."""
    COMPONENT = "component"
    ANNOTATION = "annotation"
    TEST = "test"
    DECISION = "decision"
    CONTEXT = "context"
    VIEW = "view"
    CHECKPOINT = "checkpoint"


class EdgeType(str, Enum):
    """Types of edges in the concept graph."""
    HAS_ANNOTATION = "has_annotation"
    CALLS = "calls"
    DEPENDS_ON = "depends_on"
    TESTS = "tests"
    IMPLEMENTS = "implements"
    VERIFIED_BY = "verified_by"
    CONTRADICTS = "contradicts"
    RELATED_TO = "related_to"
    EVOLVED_FROM = "evolved_from"
    COGNITION_BURDEN = "cognition_burden"
    FREQUENTLY_CO_ACCESSED = "frequently_co_accessed"


class Node:
    """Base class for all nodes in the concept graph."""
    
    def __init__(self, id: str, node_type: NodeType, properties: Dict[str, Any] = None):
        self.id = id
        self.node_type = node_type
        self.properties = properties or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary representation."""
        return {
            "id": self.id,
            "type": self.node_type,
            **self.properties
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Node':
        """Create node from dictionary representation."""
        node_id = data.pop("id")
        node_type = data.pop("type")
        return cls(node_id, node_type, data)


class ConceptNode(Node):
    """Node representing a software component (function, class, module)."""
    
    def __init__(self, id: str, component_type: str, file_path: str, 
                 name: str, component_info: Dict[str, Any] = None, 
                 start_line: int = None, end_line: int = None, actual_start_line: int = None,
                 properties: Dict[str, Any] = None):
        super().__init__(id, NodeType.COMPONENT, properties or {})
        self.component_type = component_type
        self.file_path = file_path
        self.name = name
        self.component_info = component_info or {}
        self.start_line = start_line
        self.end_line = end_line
        self.actual_start_line = actual_start_line
        
        # Update properties
        self.properties.update({
            "component_type": component_type,
            "file_path": file_path,
            "name": name
        })
        if component_info:
            self.properties["component_info"] = component_info
        if start_line is not None:
            self.properties["start_line"] = start_line
        if end_line is not None:
            self.properties["end_line"] = end_line
        if actual_start_line is not None:
            self.properties["actual_start_line"] = actual_start_line


class AnnotationNode(Node):
    """Node representing a COP annotation."""
    
    def __init__(self, id: str, annotation_type: str, value: Any,
                 metadata: Dict[str, Any] = None, properties: Dict[str, Any] = None):
        super().__init__(id, NodeType.ANNOTATION, properties or {})
        self.annotation_type = annotation_type
        self.value = value
        self.metadata = metadata or {}
        
        # Update properties
        self.properties.update({
            "annotation_type": annotation_type,
            "value": value,
            "metadata": self.metadata
        })


class Edge:
    """Base class for all edges in the concept graph."""
    
    def __init__(self, source_id: str, target_id: str, edge_type: EdgeType,
                 properties: Dict[str, Any] = None):
        self.source_id = source_id
        self.target_id = target_id
        self.edge_type = edge_type
        self.properties = properties or {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert edge to dictionary representation."""
        return {
            "source": self.source_id,
            "target": self.target_id,
            "type": self.edge_type,
            **self.properties
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Edge':
        """Create edge from dictionary representation."""
        source_id = data.pop("source")
        target_id = data.pop("target")
        edge_type = data.pop("type")
        return cls(source_id, target_id, edge_type, data)


class RelationshipEdge(Edge):
    """Edge representing a relationship between nodes."""
    
    def __init__(self, source_id: str, target_id: str, edge_type: EdgeType,
                 weight: float = 1.0, properties: Dict[str, Any] = None):
        super().__init__(source_id, target_id, edge_type, properties or {})
        self.weight = weight
        self.properties["weight"] = weight


class ConceptGraph:
    """Graph representation of COP concepts and their relationships."""
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize a new concept graph.
        
        Args:
            db_path: Optional path to SQLite database for persistence
        """
        self.nodes: Dict[str, Node] = {}
        self.edges: List[Edge] = []
        self.db_path = db_path
        
        # Initialize database if path provided
        if db_path:
            self._init_db()
    
    def _init_db(self):
        """Initialize the SQLite database for graph storage."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create nodes table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS nodes (
            id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            properties TEXT NOT NULL
        )
        ''')
        
        # Create edges table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS edges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            target TEXT NOT NULL,
            type TEXT NOT NULL,
            properties TEXT NOT NULL,
            FOREIGN KEY (source) REFERENCES nodes(id),
            FOREIGN KEY (target) REFERENCES nodes(id)
        )
        ''')
        
        # Create indices for faster queries
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_nodes_type ON nodes(type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_edges_source ON edges(source)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_edges_target ON edges(target)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_edges_type ON edges(type)')
        
        conn.commit()
        conn.close()
    
    def add_node(self, node: Node) -> Node:
        """
        Add a node to the graph.
        
        Args:
            node: Node to add
            
        Returns:
            The added node
        """
        self.nodes[node.id] = node
        
        # Persist to database if available
        if self.db_path:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'INSERT OR REPLACE INTO nodes (id, type, properties) VALUES (?, ?, ?)',
                (node.id, node.node_type, json.dumps(node.properties))
            )
            
            conn.commit()
            conn.close()
        
        return node
    
    def add_edge(self, edge: Edge) -> Edge:
        """
        Add an edge to the graph.
        
        Args:
            edge: Edge to add
            
        Returns:
            The added edge
        """
        self.edges.append(edge)
        
        # Persist to database if available
        if self.db_path:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                'INSERT INTO edges (source, target, type, properties) VALUES (?, ?, ?, ?)',
                (edge.source_id, edge.target_id, edge.edge_type, json.dumps(edge.properties))
            )
            
            conn.commit()
            conn.close()
        
        return edge
    
    def get_node(self, node_id: str) -> Optional[Node]:
        """
        Get a node by ID.
        
        Args:
            node_id: ID of the node to get
            
        Returns:
            The node, or None if not found
        """
        # Check in-memory cache first
        if node_id in self.nodes:
            return self.nodes[node_id]
        
        # Try database if available
        if self.db_path:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('SELECT type, properties FROM nodes WHERE id = ?', (node_id,))
            result = cursor.fetchone()
            
            conn.close()
            
            if result:
                node_type, properties_json = result
                properties = json.loads(properties_json)
                return Node.from_dict({"id": node_id, "type": node_type, **properties})
        
        return None
    
    def get_edges(self, source_id: Optional[str] = None, target_id: Optional[str] = None,
                 edge_type: Optional[EdgeType] = None) -> List[Edge]:
        """
        Get edges matching the given criteria.
        
        Args:
            source_id: Optional source node ID to filter by
            target_id: Optional target node ID to filter by
            edge_type: Optional edge type to filter by
            
        Returns:
            List of matching edges
        """
        # If using in-memory storage, filter edges directly
        if not self.db_path:
            result = self.edges
            
            if source_id:
                result = [e for e in result if e.source_id == source_id]
            
            if target_id:
                result = [e for e in result if e.target_id == target_id]
            
            if edge_type:
                result = [e for e in result if e.edge_type == edge_type]
            
            return result
        
        # Otherwise, query the database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = 'SELECT source, target, type, properties FROM edges WHERE 1=1'
        params = []
        
        if source_id:
            query += ' AND source = ?'
            params.append(source_id)
        
        if target_id:
            query += ' AND target = ?'
            params.append(target_id)
        
        if edge_type:
            query += ' AND type = ?'
            params.append(edge_type)
        
        cursor.execute(query, params)
        results = cursor.fetchall()
        
        conn.close()
        
        return [Edge.from_dict({
            "source": source,
            "target": target,
            "type": edge_type,
            **json.loads(properties)
        }) for source, target, edge_type, properties in results]
    
    def build_from_annotations(self, annotations: List[AnnotationInfo]) -> None:
        """
        Build the concept graph from a list of annotations.
        
        Args:
            annotations: List of annotations extracted from code
        """
        # Group annotations by component
        components = {}
        
        for anno in annotations:
            if anno.component_name not in components:
                # Create a new component node
                component_id = f"component:{anno.component_name}"
                component = ConceptNode(
                    id=component_id,
                    component_type=anno.component_type,
                    file_path=anno.file_path,
                    name=anno.component_name,
                    component_info=anno.component_info,
                    start_line=anno.start_line,
                    end_line=anno.end_line,
                    actual_start_line=anno.actual_start_line
                )
                components[anno.component_name] = component
                self.add_node(component)
            
            # Create annotation node
            annotation_id = f"annotation:{anno.annotation_type}:{anno.component_name}:{hash(str(anno.value))}"
            annotation = AnnotationNode(
                id=annotation_id,
                annotation_type=anno.annotation_type,
                value=anno.value,
                metadata=anno.metadata,
                properties={
                    "line_number": anno.line_number,
                    "file_path": anno.file_path
                }
            )
            self.add_node(annotation)
            
            # Create edge from component to annotation
            edge = RelationshipEdge(
                source_id=f"component:{anno.component_name}",
                target_id=annotation_id,
                edge_type=EdgeType.HAS_ANNOTATION
            )
            self.add_edge(edge)
    
    def query_components(self, annotation_type: Optional[str] = None,
                        annotation_value: Optional[str] = None,
                        component_type: Optional[str] = None) -> List[ConceptNode]:
        """
        Query components based on criteria.
        
        Args:
            annotation_type: Optional annotation type to filter by
            annotation_value: Optional annotation value to filter by
            component_type: Optional component type to filter by
            
        Returns:
            List of matching component nodes
        """
        # Start with all component nodes
        components = [node for node in self.nodes.values() 
                    if node.node_type == NodeType.COMPONENT]
        
        # Filter by component type if specified
        if component_type:
            components = [c for c in components 
                         if c.properties.get("component_type") == component_type]
        
        # If no annotation filters, return components
        if not annotation_type and not annotation_value:
            return components
        
        # Get component-annotation relationships
        result = []
        
        for component in components:
            # Get annotations for this component
            edges = self.get_edges(source_id=component.id, edge_type=EdgeType.HAS_ANNOTATION)
            
            for edge in edges:
                annotation = self.get_node(edge.target_id)
                
                if not annotation:
                    continue
                
                # Check annotation type
                if annotation_type and annotation.properties.get("annotation_type") != annotation_type:
                    continue
                
                # Check annotation value
                if annotation_value and str(annotation.properties.get("value")) != annotation_value:
                    continue
                
                # Add component to results
                result.append(component)
                break  # No need to check other annotations for this component
        
        return result
    
    def query_annotations(self, component_id: Optional[str] = None,
                         annotation_type: Optional[str] = None) -> List[AnnotationNode]:
        """
        Query annotations based on criteria.
        
        Args:
            component_id: Optional component ID to filter by
            annotation_type: Optional annotation type to filter by
            
        Returns:
            List of matching annotation nodes
        """
        # Start with all annotation nodes
        annotations = [node for node in self.nodes.values() 
                      if node.node_type == NodeType.ANNOTATION]
        
        # Filter by annotation type if specified
        if annotation_type:
            annotations = [a for a in annotations 
                          if a.properties.get("annotation_type") == annotation_type]
        
        # If no component filter, return annotations
        if not component_id:
            return annotations
        
        # Get annotations for the specific component
        result = []
        edges = self.get_edges(source_id=component_id, edge_type=EdgeType.HAS_ANNOTATION)
        
        for edge in edges:
            annotation = self.get_node(edge.target_id)
            
            if annotation and (not annotation_type or 
                              annotation.properties.get("annotation_type") == annotation_type):
                result.append(annotation)
        
        return result
    
    def export_to_json(self, file_path: str) -> None:
        """
        Export the graph to a JSON file.
        
        Args:
            file_path: Path to save the JSON file
        """
        data = {
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": [edge.to_dict() for edge in self.edges]
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    @classmethod
    def import_from_json(cls, file_path: str) -> 'ConceptGraph':
        """
        Import a graph from a JSON file.
        
        Args:
            file_path: Path to the JSON file
            
        Returns:
            The imported graph
        """
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        graph = cls()
        
        # Import nodes
        for node_data in data["nodes"]:
            node_id = node_data["id"]
            node_type = node_data["type"]
            
            if node_type == NodeType.COMPONENT:
                node = ConceptNode(
                    id=node_id,
                    component_type=node_data.get("component_type", "unknown"),
                    file_path=node_data.get("file_path", ""),
                    name=node_data.get("name", ""),
                    component_info=node_data.get("component_info"),
                    start_line=node_data.get("start_line"),
                    end_line=node_data.get("end_line"),
                    actual_start_line=node_data.get("actual_start_line"),
                    properties=node_data
                )
            elif node_type == NodeType.ANNOTATION:
                node = AnnotationNode(
                    id=node_id,
                    annotation_type=node_data.get("annotation_type", "unknown"),
                    value=node_data.get("value"),
                    metadata=node_data.get("metadata", {}),
                    properties=node_data
                )
            else:
                node = Node(node_id, node_type, node_data)
            
            graph.add_node(node)
        
        # Import edges
        for edge_data in data["edges"]:
            edge = Edge(
                source_id=edge_data["source"],
                target_id=edge_data["target"],
                edge_type=edge_data["type"],
                properties=edge_data
            )
            
            graph.add_edge(edge)
        
        return graph


if __name__ == "__main__":
    # Simple CLI for testing
    import argparse
    from .extractor import extract_annotations_from_directory
    
    parser = argparse.ArgumentParser(description="Build concept graph from Python code")
    parser.add_argument("directory", help="Directory to analyze")
    parser.add_argument("--output", help="Output file for graph (JSON)")
    parser.add_argument("--db", help="SQLite database file for persistent storage")
    args = parser.parse_args()
    
    # Extract annotations
    annotations = extract_annotations_from_directory(args.directory)
    
    # Build graph
    graph = ConceptGraph(args.db)
    graph.build_from_annotations(annotations)
    
    # Save to JSON if requested
    if args.output:
        graph.export_to_json(args.output)
        print(f"Graph exported to {args.output}")
    
    # Print summary
    component_count = len([n for n in graph.nodes.values() if n.node_type == NodeType.COMPONENT])
    annotation_count = len([n for n in graph.nodes.values() if n.node_type == NodeType.ANNOTATION])
    edge_count = len(graph.edges)
    
    print(f"Graph built with:")
    print(f"- {component_count} components")
    print(f"- {annotation_count} annotations")
    print(f"- {edge_count} relationships")