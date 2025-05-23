"""
Test script for default annotations functionality.
"""

from cop_python.analysis.extractor import extract_annotations_from_file
from cop_python.analysis.graph import ConceptGraph
from cop_python.analysis.exporter import JSONLExporter
import os

def main():
    # Extract annotations with defaults
    print("Testing default annotations...")
    
    # Define default annotations
    default_annotations = {
        "implementation_status": "UNIMPLEMENTED",
        "risk": "unknown"
    }
    
    # Extract without defaults first
    print("\n1. Without default annotations:")
    annotations_normal = extract_annotations_from_file("test_annotated_module.py")
    print(f"Found {len(annotations_normal)} annotations")
    
    # Group by component and annotation type for analysis
    components_normal = {}
    for anno in annotations_normal:
        if anno.component_name not in components_normal:
            components_normal[anno.component_name] = set()
        components_normal[anno.component_name].add(anno.annotation_type)
    
    print("Components and their annotation types:")
    for component, types in sorted(components_normal.items()):
        print(f"  {component}: {sorted(types)}")
    
    # Extract with defaults
    print("\n2. With default annotations:")
    annotations_with_defaults = extract_annotations_from_file(
        "test_annotated_module.py", 
        default_annotations=default_annotations
    )
    print(f"Found {len(annotations_with_defaults)} annotations")
    
    # Group by component and annotation type for analysis
    components_with_defaults = {}
    for anno in annotations_with_defaults:
        if anno.component_name not in components_with_defaults:
            components_with_defaults[anno.component_name] = {}
        components_with_defaults[anno.component_name][anno.annotation_type] = anno.metadata.get("is_default", False)
    
    print("Components and their annotation types (D = default):")
    for component, types in sorted(components_with_defaults.items()):
        type_info = []
        for annotation_type, is_default in sorted(types.items()):
            marker = " (D)" if is_default else ""
            type_info.append(f"{annotation_type}{marker}")
        print(f"  {component}: {type_info}")
    
    # Show which components got default annotations
    print("\n3. Default annotations added:")
    for anno in annotations_with_defaults:
        if anno.metadata.get("is_default", False):
            print(f"  {anno.component_name}: {anno.annotation_type} = {anno.value}")
    
    # Test with graph and export
    print("\n4. Building graph with defaults...")
    graph = ConceptGraph()
    graph.build_from_annotations(annotations_with_defaults)
    
    # Export to see the results
    output_dir = "test_defaults_output"
    os.makedirs(output_dir, exist_ok=True)
    
    exporter = JSONLExporter(output_dir)
    counts = exporter.export_graph(graph)
    
    print(f"Exported {sum(counts['nodes'].values())} nodes and {sum(counts['edges'].values())} edges")
    print(f"Check {output_dir}/ for exported data with default annotations")

if __name__ == "__main__":
    main()