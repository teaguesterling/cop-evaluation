"""
Static analysis tools for extracting COP annotations from Python code.

This module provides tools for:
1. Parsing Python source code to extract COP annotations
2. Building a concept graph from annotations
3. Exporting the concept graph to various formats (JSONL, DuckDB)
4. Querying the concept graph
"""

from .extractor import extract_annotations_from_file, extract_annotations_from_directory, AnnotationInfo
from .graph import (
    ConceptGraph, ConceptNode, AnnotationNode, RelationshipEdge,
    NodeType, EdgeType, Node, Edge
)
from .exporter import JSONLExporter, DuckDBLoader

__all__ = [
    # Extractor
    "extract_annotations_from_file", 
    "extract_annotations_from_directory",
    "AnnotationInfo",
    
    # Graph
    "ConceptGraph",
    "ConceptNode",
    "AnnotationNode", 
    "RelationshipEdge",
    "NodeType",
    "EdgeType",
    "Node",
    "Edge",
    
    # Exporter
    "JSONLExporter",
    "DuckDBLoader"
]