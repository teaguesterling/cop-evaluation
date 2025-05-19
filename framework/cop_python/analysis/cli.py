#!/usr/bin/env python3
"""
Command-line interface for the COP static analysis toolkit.

This module provides a command-line interface for extracting COP annotations
from Python code, building a concept graph, and exporting it to various formats.
"""

import os
import sys
import argparse
import json
from typing import Dict, List, Any, Optional
from pathlib import Path

from .extractor import extract_annotations_from_file, extract_annotations_from_directory
from .graph import ConceptGraph, NodeType, EdgeType
from .exporter import JSONLExporter, DuckDBLoader


def extract_command(args):
    """Extract COP annotations from Python code."""
    path = args.path
    recursive = not args.no_recursive
    output_file = args.output
    
    if os.path.isfile(path):
        annotations = extract_annotations_from_file(path)
    else:
        annotations = extract_annotations_from_directory(path, recursive)
    
    # Print summary
    print(f"Found {len(annotations)} annotations:")
    
    # Group by type
    by_type = {}
    for anno in annotations:
        if anno.annotation_type not in by_type:
            by_type[anno.annotation_type] = 0
        by_type[anno.annotation_type] += 1
    
    for anno_type, count in by_type.items():
        print(f"- {anno_type}: {count}")
    
    # Export to JSON if requested
    if output_file:
        with open(output_file, 'w') as f:
            json.dump([anno._asdict() for anno in annotations], f, indent=2)
        print(f"Annotations exported to {output_file}")
    
    return 0


def build_command(args):
    """Build a concept graph from Python code."""
    path = args.path
    recursive = not args.no_recursive
    output_file = args.output
    
    # Extract annotations
    if os.path.isfile(path):
        annotations = extract_annotations_from_file(path)
    else:
        annotations = extract_annotations_from_directory(path, recursive)
    
    # Build graph
    graph = ConceptGraph()
    graph.build_from_annotations(annotations)
    
    # Print summary
    component_count = len([n for n in graph.nodes.values() if n.node_type == NodeType.COMPONENT])
    annotation_count = len([n for n in graph.nodes.values() if n.node_type == NodeType.ANNOTATION])
    edge_count = len(graph.edges)
    
    print(f"Built concept graph:")
    print(f"- {component_count} components")
    print(f"- {annotation_count} annotations")
    print(f"- {edge_count} relationships")
    
    # Export to JSON if requested
    if output_file:
        graph.export_to_json(output_file)
        print(f"Graph exported to {output_file}")
    
    return 0


def export_command(args):
    """Export a concept graph to JSONL files."""
    path = args.path
    recursive = not args.no_recursive
    output_dir = args.output_dir
    db_path = args.db
    
    # Extract annotations
    if os.path.isfile(path):
        annotations = extract_annotations_from_file(path)
    else:
        annotations = extract_annotations_from_directory(path, recursive)
    
    # Build graph
    graph = ConceptGraph()
    graph.build_from_annotations(annotations)
    
    # Export to JSONL
    exporter = JSONLExporter(output_dir)
    counts = exporter.export_graph(graph)
    
    # Print summary
    print(f"Exported concept graph to {output_dir}:")
    print(f"- Nodes: {sum(counts['nodes'].values())}")
    for node_type, count in counts['nodes'].items():
        print(f"  - {node_type}: {count}")
    print(f"- Edges: {sum(counts['edges'].values())}")
    for edge_type, count in counts['edges'].items():
        print(f"  - {edge_type}: {count}")
    
    # Load into DuckDB if requested
    if db_path:
        try:
            print(f"Loading data into DuckDB at {db_path}...")
            loader = DuckDBLoader(db_path)
            loader.load_from_jsonl(output_dir)
            print("Loading complete")
        except ImportError:
            print("Skipping DuckDB loading: DuckDB not installed")
            print("To use this feature, install duckdb with: pip install duckdb")
    
    return 0


def load_command(args):
    """Load JSONL files into DuckDB."""
    jsonl_dir = args.jsonl_dir
    db_path = args.db
    
    # Load into DuckDB
    try:
        loader = DuckDBLoader(db_path)
        counts = loader.load_from_jsonl(jsonl_dir)
        
        # Print summary
        print(f"Loaded concept graph into DuckDB at {db_path}:")
        print(f"- Nodes: {sum(counts['nodes'].values())}")
        for node_type, count in counts['nodes'].items():
            print(f"  - {node_type}: {count}")
        print(f"- Edges: {sum(counts['edges'].values())}")
        for edge_type, count in counts['edges'].items():
            print(f"  - {edge_type}: {count}")
    except ImportError:
        print("Error: DuckDB not installed")
        print("To use this feature, install duckdb with: pip install duckdb")
        return 1
    
    return 0


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        prog="cop-analysis",
        description="COP static analysis toolkit",
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Extract command
    extract_parser = subparsers.add_parser("extract", help="Extract COP annotations")
    extract_parser.add_argument("path", help="File or directory to analyze")
    extract_parser.add_argument("--no-recursive", action="store_true", help="Don't scan directories recursively")
    extract_parser.add_argument("--output", help="Output file for annotations (JSON)")
    extract_parser.set_defaults(func=extract_command)
    
    # Build command
    build_parser = subparsers.add_parser("build", help="Build concept graph")
    build_parser.add_argument("path", help="File or directory to analyze")
    build_parser.add_argument("--no-recursive", action="store_true", help="Don't scan directories recursively")
    build_parser.add_argument("--output", help="Output file for graph (JSON)")
    build_parser.set_defaults(func=build_command)
    
    # Export command
    export_parser = subparsers.add_parser("export", help="Export concept graph to JSONL files")
    export_parser.add_argument("path", help="File or directory to analyze")
    export_parser.add_argument("--no-recursive", action="store_true", help="Don't scan directories recursively")
    export_parser.add_argument("--output-dir", required=True, help="Output directory for JSONL files")
    export_parser.add_argument("--db", help="DuckDB database file for loading (optional)")
    export_parser.set_defaults(func=export_command)
    
    # Load command
    load_parser = subparsers.add_parser("load", help="Load JSONL files into DuckDB")
    load_parser.add_argument("jsonl_dir", help="Directory containing JSONL files")
    load_parser.add_argument("--db", required=True, help="DuckDB database file")
    load_parser.set_defaults(func=load_command)
    
    # Parse arguments and run command
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())