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
   - Supports default annotation values for comprehensive coverage

2. **Test Extractor** (`test_extractor.py`): Extracts test-component relationships
   - Parses test decorators (`@test_for`, `@test_invariant`, `@test_risk`, etc.)
   - Links tests to specific components and annotations
   - Tracks test types and verification coverage
   - Integrates with metrics system for test analysis

3. **Graph** (`graph.py`): Builds a concept graph from extracted annotations and tests
   - Represents components, annotations, and tests as nodes
   - Maintains relationships and verification edges
   - Provides query capabilities for finding related concepts
   - Tracks verification status and test coverage

4. **Metrics** (`metrics.py`): Calculates code quality metrics
   - Complexity metrics (cyclomatic, cognitive)
   - Size metrics (lines of code, parameters, variables)
   - Dependency metrics (imports, function calls)
   - Pluggable provider system for extensibility

5. **Exporter** (`exporter.py`): Exports the concept graph to formats for further analysis
   - Exports to JSONL files (one per node/edge type)
   - Designed for easy import into DuckDB with DuckPGQ
   - Supports incremental exports and metadata tracking

6. **CLI** (`cli.py`): Command-line interface for the static analysis tools
   - Extract annotations from files or directories
   - Extract test relationships and verification status
   - Build concept graphs with annotations and tests
   - Export to different formats with comprehensive statistics

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

### Python API

```python
# Extract annotations from a file
from cop_python.analysis.extractor import extract_annotations_from_file
annotations = extract_annotations_from_file("path/to/file.py")

# Extract test relationships
from cop_python.analysis.test_extractor import extract_test_relationships_from_file
test_relationships = extract_test_relationships_from_file("path/to/test_file.py")

# Build a concept graph with both annotations and tests
from cop_python.analysis.graph import ConceptGraph
graph = ConceptGraph()
graph.build_from_annotations(annotations)
graph.build_from_test_relationships(test_relationships)

# Check verification status
status = graph.get_verification_status("component:MyClass.method")
print(f"Tests: {status['total_tests']}, Coverage: {status['annotation_coverage']}")

# Export to JSONL
from cop_python.analysis.exporter import JSONLExporter
exporter = JSONLExporter("output_dir")
exporter.export_graph(graph)
```

### Test Relationship Decorators

The test extractor recognizes several decorator patterns:

```python
# Basic component testing
@test_for("MyClass.method")
def test_basic_functionality():
    pass

# Specific annotation testing
@test_invariant("MyClass.method", "x > 0")
def test_invariant_maintained():
    pass

@test_risk("MyClass.method", "HIGH")
def test_high_risk_scenarios():
    pass

@test_implementation_status("MyClass.method", "IMPLEMENTED")
def test_implemented_features():
    pass

# With test type specification
@test_for("MyClass.method", test_type="integration")
def test_integration():
    pass
```

## Command-line Interface

### Basic Commands

```bash
# Extract annotations and print summary
python -m cop_python.analysis.cli extract path/to/code

# Build and export a concept graph
python -m cop_python.analysis.cli build path/to/code --output graph.json

# Export to JSONL for DuckDB
python -m cop_python.analysis.cli export path/to/code --output-dir output_dir
```

### Test Relationship Commands

```bash
# Extract test relationships from test files
python -m cop_python.analysis.cli test-extract tests/ --output test_relationships.json

# Build concept graph with both annotations and tests
python -m cop_python.analysis.cli test-build src/ --test-path tests/ --output full_graph.json

# Extract from same directory (annotations and tests together)
python -m cop_python.analysis.cli test-build project_root/ --output combined_graph.json
```

### Advanced Options

```bash
# Add default annotations for incomplete components
python -m cop_python.analysis.cli extract src/ \
  --default-implementation-status "PROTOTYPE" \
  --default-risk "MEDIUM"

# Non-recursive scanning
python -m cop_python.analysis.cli test-extract tests/ --no-recursive

# Export with DuckDB loading
python -m cop_python.analysis.cli export src/ \
  --output-dir jsonl_output \
  --db concept_graph.db
```

### Example Output

```
$ python -m cop_python.analysis.cli test-extract tests/
Found 15 test relationships:

By test type:
- unit: 12
- integration: 3

Target components: 5
- MyClass.calculate: 4 tests
- MyClass.validate: 3 tests
- DataProcessor.process: 2 tests
- Utils.helper: 3 tests
- Config.load: 3 tests
Tests with annotation references: 8

$ python -m cop_python.analysis.cli test-build src/ --test-path tests/
Built concept graph:
- 12 components
- 28 annotations
- 15 tests
- 55 relationships
- 8/12 components have tests (66.7%)
```

## Implementation Status

The following features have been implemented:

1. ✅ **Selective Component Information** - Extract only essential information instead of full source
2. ✅ **Code Metrics System** - Calculate code quality metrics (complexity, size, etc.)
3. ✅ **Default Annotation Values** - Support for default values (e.g., implementation_status)
4. ✅ **Test Linkage Analysis** - Connect components to their tests via test decorators
5. ⏳ **Annotation Modification** - Update annotations based on test results (planned)

## Graph Database Integration

The toolkit is designed for integration with graph databases:

- **DuckDB with DuckPGQ**: Export JSONL files for graph analysis
- **Property Graph Model**: Nodes (components, annotations, tests) and edges (relationships, verification)
- **Graph Queries**: Find related concepts, verification coverage, dependency analysis

Example DuckDB queries:

```sql
-- Find all tests for high-risk components
SELECT t.test_name, c.name, a.value as risk_level
FROM test t
JOIN verified_by vb ON t.id = vb.target
JOIN component c ON vb.source = c.id  
JOIN has_annotation ha ON c.id = ha.source
JOIN annotation a ON ha.target = a.id
WHERE a.annotation_type = 'risk' AND a.value = 'HIGH';

-- Calculate verification coverage by component
SELECT c.name, COUNT(DISTINCT t.id) as test_count
FROM component c
LEFT JOIN verified_by vb ON c.id = vb.source
LEFT JOIN test t ON vb.target = t.id
GROUP BY c.name
ORDER BY test_count DESC;
```

See the [Implementation Plan](../docs/Static%20Analysis%20Implementation%20Plan.md) for details.