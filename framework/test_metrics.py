"""
Test script for the COP code metrics.
"""

import os
import json
from cop_python.analysis.extractor import extract_annotations_from_file
from cop_python.analysis.metrics import get_default_metrics_providers
from cop_python.analysis.graph import ConceptGraph
from cop_python.analysis.exporter import JSONLExporter

def main():
    # Extract annotations from the test module with metrics
    print("Extracting annotations with metrics...")
    annotations = extract_annotations_from_file("test_annotated_module.py")
    
    # Print extracted metrics for each component
    print(f"Found {len(annotations)} annotations with metrics:")
    
    # Group by component to avoid duplicates
    components = {}
    for anno in annotations:
        if anno.component_name not in components:
            components[anno.component_name] = (anno.component_type, anno.metrics)
    
    # Print metrics for each component
    for component_name, (component_type, metrics) in sorted(components.items()):
        print(f"\n{component_name} ({component_type})")
        print(f"  Metrics:")
        
        # Print size metrics
        if "lines_of_code" in metrics:
            print(f"  - Size metrics:")
            print(f"    - Lines of code: {metrics.get('lines_of_code')}")
            print(f"    - Statement count: {metrics.get('statement_count')}")
            
            if component_type == "class":
                print(f"    - Method count: {metrics.get('method_count')}")
                print(f"    - Attribute count: {metrics.get('attribute_count')}")
            elif component_type in ("function", "method"):
                print(f"    - Parameter count: {metrics.get('parameter_count')}")
                print(f"    - Local variable count: {metrics.get('local_variable_count')}")
                print(f"    - Return count: {metrics.get('return_count')}")
        
        # Print complexity metrics for functions/methods
        if component_type in ("function", "method") and "cyclomatic_complexity" in metrics:
            print(f"  - Complexity metrics:")
            print(f"    - Cyclomatic complexity: {metrics.get('cyclomatic_complexity')}")
            print(f"    - Cognitive complexity: {metrics.get('cognitive_complexity')}")
        
        # Print dependency metrics
        if "function_call_count" in metrics:
            print(f"  - Dependency metrics:")
            print(f"    - Function call count: {metrics.get('function_call_count')}")
    
    # Build concept graph and export
    print("\nBuilding concept graph...")
    graph = ConceptGraph()
    graph.build_from_annotations(annotations)
    
    # Export to JSONL
    output_dir = "test_metrics_output"
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Exporting to JSONL in {output_dir}...")
    exporter = JSONLExporter(output_dir)
    counts = exporter.export_graph(graph)
    
    print("Export complete.")
    print(f"- Exported {sum(counts['nodes'].values())} nodes")
    print(f"- Exported {sum(counts['edges'].values())} edges")

if __name__ == "__main__":
    main()