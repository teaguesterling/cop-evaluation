# COP Static Analysis

This module provides static analysis tools for Concept-Oriented Programming (COP) annotations in Python code.

## Overview

The static analysis toolkit extracts COP annotations from Python code using Abstract Syntax Tree (AST) parsing without executing the code. This enables:

- Documentation generation
- Concept graph analysis
- Intent-implementation tracking
- Risk management
- Development planning

## Components

The static analysis toolkit consists of several key components:

1. **Extractor** (`extractor.py`): Parses Python code to extract COP annotations
   - Uses AST parsing to analyze code without execution
   - Extracts selective component information (docstrings, signatures, methods)
   - Captures line boundary information for easy access to full implementations

2. **Graph** (`graph.py`): Builds a concept graph from extracted annotations
   - Represents components and annotations as nodes
   - Maintains relationships as edges
   - Provides query capabilities for finding related concepts

3. **Exporter** (`exporter.py`): Exports the concept graph to formats for further analysis
   - Exports to JSONL files (one per node/edge type)
   - Designed for easy import into DuckDB with DuckPGQ

4. **CLI** (`cli.py`): Command-line interface for the static analysis tools
   - Extract annotations from files or directories
   - Build concept graphs
   - Export to different formats

## Selective Component Information

Instead of storing the full source code of each component, we extract only essential information:

- **Functions/Methods:**
  - Docstring
  - Parameter information (names, types)
  - Return type
  - Line boundaries (for full extraction if needed)

- **Classes:**
  - Docstring
  - Method names
  - Attribute names
  - Base classes
  - Line boundaries

This approach significantly reduces the size of the concept graph while retaining all necessary information for analysis. For AI tools that need the full implementation, the line boundaries enable precise extraction from the original source files.

## Usage

```python
# Extract annotations from a file
from cop_python.analysis.extractor import extract_annotations_from_file
annotations = extract_annotations_from_file("path/to/file.py")

# Build a concept graph
from cop_python.analysis.graph import ConceptGraph
graph = ConceptGraph()
graph.build_from_annotations(annotations)

# Export to JSONL
from cop_python.analysis.exporter import JSONLExporter
exporter = JSONLExporter("output_dir")
exporter.export_graph(graph)
```

## Command-line Interface

```bash
# Extract annotations and print summary
python -m cop_python.analysis.cli extract path/to/code

# Build and export a concept graph
python -m cop_python.analysis.cli build path/to/code --output graph.json

# Export to JSONL for DuckDB
python -m cop_python.analysis.cli export path/to/code --output output_dir
```

## Future Enhancements

The following enhancements are planned:

1. ✅ **Selective Component Information** - Extract only essential information instead of full source
2. **Code Metrics System** - Calculate code quality metrics (complexity, size, etc.)
3. **Default Annotation Values** - Support for default values (e.g., implementation_status)
4. **Test Linkage Analysis** - Connect components to their tests
5. **Annotation Modification** - Update annotations based on test results

See the [Implementation Plan](../docs/Static%20Analysis%20Implementation%20Plan.md) for details.