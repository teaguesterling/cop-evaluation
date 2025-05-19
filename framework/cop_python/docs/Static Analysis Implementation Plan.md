# COP Static Analysis Implementation Plan

This document outlines the current understanding of the COP system and detailed plans for implementing improvements to the static analysis toolkit.

## Current Understanding of the COP System

### Core Components

1. **COP Framework**
   - `cop_python/core.py`: Core classes like `COPAnnotation`, `COPSingletonAnnotation`, and `ConceptAnnotations`
   - `cop_python/runtime.py`: Runtime infrastructure with `COPSystem`, `COPNamespace` (fixed bug in `__getitem__`)
   - `cop_python/annotations.py`: Actual annotation implementations (intent, risk, etc.)

2. **Testing Framework**
   - `cop_python/testing/`: Testing infrastructure for verifying annotations
   - `cop_python/testing/verification.py`: Registry for linking tests to annotations
   - `cop_python/testing/annotations.py`: Test-specific annotation extensions
   - `cop_python/testing/assertions.py`: Assertion functions for tests

3. **Utilities**
   - `cop_python/utils.py`: Helper functions like `get_annotations_namespace`

4. **New Static Analysis**
   - `cop_python/analysis/extractor.py`: AST-based extraction of annotations
   - `cop_python/analysis/graph.py`: Concept graph representation
   - `cop_python/analysis/exporter.py`: JSONL export for graph data
   - `cop_python/analysis/cli.py`: Command-line interface

### Current Functionality

1. **Annotation System**
   - Decorators for adding metadata to code components
   - Runtime storage in `__cop_annotations__` attribute
   - Hierarchical inheritance of annotations

2. **Testing System**
   - Verification of annotations through tests
   - Registry for tracking test-annotation relationships
   - Reporting capabilities for verification status

3. **Static Analysis**
   - AST-based extraction of annotations (no runtime execution)
   - Building a concept graph from extracted annotations
   - Exporting to JSONL format for future graph database storage

## Implementation Plan for Improvements

### 1. Selective Component Information

Instead of exporting the entire source code of components, extract only relevant information:

```python
class COPAnnotationVisitor(ast.NodeVisitor):
    def _extract_component_info(self, node):
        """Extract only relevant information for a component."""
        # Common fields
        info = {
            "name": node.name,
            "docstring": ast.get_docstring(node),
            "lineno": node.lineno,
        }
        
        # Function/method specific
        if isinstance(node, ast.FunctionDef):
            # Extract signature (args, return annotations)
            info["signature"] = self._extract_function_signature(node)
            
        # Class specific
        elif isinstance(node, ast.ClassDef):
            # Extract attributes and method names only
            info["methods"] = [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
            info["attributes"] = self._extract_class_attributes(node)
            
        # Module specific (for top-level module parsing)
        elif isinstance(node, ast.Module):
            # Extract imports and exports
            info["imports"] = self._extract_imports(node)
            info["exports"] = self._extract_exports(node)
        
        return info
        
    def _extract_function_signature(self, node):
        """Extract function signature information."""
        args = []
        for arg in node.args.args:
            arg_info = {"name": arg.arg}
            if arg.annotation:
                arg_info["annotation"] = self._format_annotation(arg.annotation)
            args.append(arg_info)
        
        returns = None
        if node.returns:
            returns = self._format_annotation(node.returns)
        
        return {
            "args": args,
            "returns": returns,
            "defaults": len(node.args.defaults),
            "vararg": node.args.vararg.arg if node.args.vararg else None,
            "kwarg": node.args.kwarg.arg if node.args.kwarg else None,
        }
    
    def _extract_class_attributes(self, node):
        """Extract class attributes from a class definition."""
        attributes = []
        
        for item in node.body:
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        attributes.append(target.id)
        
        return attributes
    
    def _extract_imports(self, node):
        """Extract import statements from a module."""
        imports = []
        
        for item in node.body:
            if isinstance(item, ast.Import):
                for name in item.names:
                    imports.append({
                        "module": name.name,
                        "alias": name.asname
                    })
            elif isinstance(item, ast.ImportFrom):
                for name in item.names:
                    imports.append({
                        "module": item.module,
                        "name": name.name,
                        "alias": name.asname
                    })
        
        return imports
    
    def _extract_exports(self, node):
        """Extract __all__ exports from a module."""
        for item in node.body:
            if (isinstance(item, ast.Assign) and 
                len(item.targets) == 1 and 
                isinstance(item.targets[0], ast.Name) and 
                item.targets[0].id == "__all__"):
                
                if isinstance(item.value, ast.List):
                    exports = []
                    for elt in item.value.elts:
                        if isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                            exports.append(elt.value)
                    return exports
        
        return None
```

### 2. Code Metrics System

Design a flexible metrics system that can calculate various code metrics:

```python
class MetricsProvider:
    """Base class for code metrics providers."""
    
    def calculate_metrics(self, component_type, ast_node, file_path):
        """Calculate metrics for a component."""
        raise NotImplementedError()

class ComplexityMetricsProvider(MetricsProvider):
    """Provides complexity metrics."""
    
    def calculate_metrics(self, component_type, ast_node, file_path):
        if component_type not in ("function", "method"):
            return {}
            
        # Calculate cyclomatic complexity
        complexity = self._calculate_cyclomatic_complexity(ast_node)
        
        # Calculate cognitive complexity
        cognitive_complexity = self._calculate_cognitive_complexity(ast_node)
        
        return {
            "cyclomatic_complexity": complexity,
            "cognitive_complexity": cognitive_complexity
        }
    
    def _calculate_cyclomatic_complexity(self, node):
        """Calculate cyclomatic complexity of a function."""
        # Count branches (if, while, for, etc.)
        # This is a simplified implementation
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.BoolOp) and isinstance(child.op, ast.And):
                complexity += len(child.values) - 1
        
        return complexity
    
    def _calculate_cognitive_complexity(self, node):
        """Calculate cognitive complexity of a function."""
        # More complex calculation involving nesting levels, etc.
        # This is a placeholder
        return self._calculate_cyclomatic_complexity(node) * 1.5

class SizeMetricsProvider(MetricsProvider):
    """Provides size-related metrics."""
    
    def calculate_metrics(self, component_type, ast_node, file_path):
        # Calculate lines of code
        loc = self._count_lines(ast_node)
        
        # Count statements
        statements = self._count_statements(ast_node)
        
        return {
            "lines_of_code": loc,
            "statement_count": statements,
        }
    
    def _count_lines(self, node):
        """Count the number of lines in a node."""
        if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
            return node.end_lineno - node.lineno + 1
        return 0
    
    def _count_statements(self, node):
        """Count the number of statements in a node."""
        count = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.Assign, ast.AugAssign, ast.Return, 
                                   ast.Raise, ast.Assert, ast.Import, 
                                   ast.ImportFrom, ast.Expr)):
                count += 1
        return count

class DependencyMetricsProvider(MetricsProvider):
    """Provides dependency-related metrics."""
    
    def calculate_metrics(self, component_type, ast_node, file_path):
        if component_type == "module":
            # Count imports
            import_count, external_count = self._count_imports(ast_node)
            
            return {
                "import_count": import_count,
                "external_dependency_count": external_count
            }
        
        return {}
    
    def _count_imports(self, node):
        """Count imports in a module."""
        import_count = 0
        external_count = 0
        
        for child in ast.walk(node):
            if isinstance(child, ast.Import):
                import_count += len(child.names)
                # Assuming anything not in stdlib is external
                for name in child.names:
                    if not self._is_stdlib(name.name):
                        external_count += 1
            elif isinstance(child, ast.ImportFrom):
                import_count += len(child.names)
                if not self._is_stdlib(child.module):
                    external_count += len(child.names)
        
        return import_count, external_count
    
    def _is_stdlib(self, module_name):
        """Check if a module is part of the standard library."""
        # This is a simplification
        stdlib_modules = {"os", "sys", "re", "math", "datetime", 
                          "collections", "json", "time", "random"}
        
        return module_name in stdlib_modules or module_name.startswith("_")
```

Integration with extractor:

```python
class COPAnnotationVisitor(ast.NodeVisitor):
    def __init__(self, file_path, source_code, metrics_providers=None):
        # ...existing code...
        self.metrics_providers = metrics_providers or []
    
    def _extract_metrics(self, node, component_type):
        """Extract metrics using all registered providers."""
        metrics = {}
        for provider in self.metrics_providers:
            try:
                provider_metrics = provider.calculate_metrics(
                    component_type, node, self.file_path
                )
                metrics.update(provider_metrics)
            except Exception as e:
                print(f"Warning: Metrics provider {provider.__class__.__name__} failed: {e}")
        
        return metrics
```

### 3. Default Annotation Values

Add support for default annotation values, especially for implementation_status:

```python
def extract_annotations_from_file(file_path, default_annotations=None):
    """
    Extract COP annotations from a Python file.
    
    Args:
        file_path: Path to the Python file
        default_annotations: Optional dict mapping annotation types to default values
        
    Returns:
        List of extracted annotations
    """
    # Normal extraction
    annotations = _extract_annotations_from_file_impl(file_path)
    
    # Apply defaults if specified
    if default_annotations:
        annotations = _apply_default_annotations(annotations, default_annotations, file_path)
    
    return annotations

def _apply_default_annotations(annotations, default_annotations, file_path):
    """Apply default annotations to components that don't have them."""
    # Group annotations by component
    components = {}
    for anno in annotations:
        if anno.component_name not in components:
            components[anno.component_name] = {}
        components[anno.component_name][anno.annotation_type] = anno
    
    # Create missing annotations with defaults
    new_annotations = list(annotations)
    for component_name, anno_dict in components.items():
        for anno_type, default_value in default_annotations.items():
            if anno_type not in anno_dict:
                # Create a default annotation
                new_anno = AnnotationInfo(
                    annotation_type=anno_type,
                    component_name=component_name,
                    component_type=_infer_component_type(component_name),
                    file_path=file_path,
                    line_number=0,  # No actual line number for default annotations
                    value=default_value,
                    metadata={"is_default": True},
                    source_code=""
                )
                new_annotations.append(new_anno)
    
    return new_annotations

def _infer_component_type(component_name):
    """Infer the component type from its name."""
    parts = component_name.split('.')
    
    # If name has multiple parts, the last part might be a method
    if len(parts) > 1:
        if len(parts) >= 3:  # module.class.method likely
            return "method"
        else:
            return "function"  # module.function likely
    
    # Single part - probably a class or module
    return "unknown"
```

CLI integration:

```python
def extract_command(args):
    """Extract COP annotations from Python code."""
    path = args.path
    recursive = not args.no_recursive
    output_file = args.output
    
    # Parse default annotations
    default_annotations = {}
    if args.default_implementation_status:
        default_annotations["implementation_status"] = args.default_implementation_status
    
    if os.path.isfile(path):
        annotations = extract_annotations_from_file(path, default_annotations)
    else:
        annotations = extract_annotations_from_directory(path, recursive, default_annotations)
    
    # Rest of the function...
```

### 4. Test Linkage Analysis

Extract test-component relationships to enhance the concept graph:

```python
class TestRelationshipExtractor(ast.NodeVisitor):
    """Extract test-to-component relationships from test code."""
    
    def __init__(self, file_path, source_code):
        self.file_path = file_path
        self.source_code = source_code
        self.module_name = self._get_module_name(file_path)
        self.relationships = []
    
    def _get_module_name(self, file_path):
        """Extract module name from file path."""
        file_path = os.path.abspath(file_path)
        
        # Try to get a proper module name by finding the package root
        for path in sys.path:
            if file_path.startswith(path):
                rel_path = os.path.relpath(file_path, path)
                module_path = os.path.splitext(rel_path)[0].replace(os.path.sep, '.')
                return module_path
        
        # Fallback: use file name without extension
        return os.path.splitext(os.path.basename(file_path))[0]
    
    def visit_FunctionDef(self, node):
        """Visit a function definition."""
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                # Check for test_for and similar decorators
                decorator_name = decorator.func.id
                if decorator_name in ("test_for", "test_invariant", "test_risk"):
                    # Extract test relationship
                    test_name = f"{self.module_name}.{node.name}"
                    target_component, annotation_ref = self._extract_test_target(decorator)
                    
                    self.relationships.append(TestRelationship(
                        test_name=test_name,
                        target_component=target_component,
                        annotation_ref=annotation_ref,
                        file_path=self.file_path,
                        line_number=node.lineno
                    ))
    
    def _extract_test_target(self, decorator):
        """Extract target component and annotation reference from a test decorator."""
        args = decorator.args
        keywords = {kw.arg: kw.value for kw in decorator.keywords}
        
        if not args:
            return None, None
        
        # First arg is usually the component
        target_component = self._extract_arg_value(args[0])
        
        # Extract annotation reference
        annotation_ref = None
        if decorator.func.id == "test_for":
            # Look for annotation type in keywords
            annotation_type = None
            annotation_value = None
            
            for key, value in keywords.items():
                if key in ("invariant", "risk", "decision"):
                    annotation_type = key
                    annotation_value = self._extract_arg_value(value)
                    break
            
            if annotation_type and annotation_value:
                annotation_ref = {
                    "type": annotation_type,
                    "value": annotation_value
                }
                
        elif decorator.func.id in ("test_invariant", "test_risk"):
            # Annotation type is in the decorator name
            annotation_type = decorator.func.id.replace("test_", "")
            # Value is usually the second arg
            if len(args) > 1:
                annotation_value = self._extract_arg_value(args[1])
                annotation_ref = {
                    "type": annotation_type,
                    "value": annotation_value
                }
        
        return target_component, annotation_ref
    
    def _extract_arg_value(self, arg):
        """Extract the value from an AST node representing a decorator argument."""
        if isinstance(arg, ast.Constant):
            return arg.value
        elif isinstance(arg, ast.Name):
            return f"<variable:{arg.id}>"
        elif isinstance(arg, ast.Attribute):
            return f"{self._extract_arg_value(arg.value)}.{arg.attr}"
        else:
            return "<complex_expression>"
```

Integration with the graph:

```python
class TestNode(Node):
    """Node representing a test."""
    
    def __init__(self, id: str, test_name: str, file_path: str, 
                 test_result: Optional[str] = None, properties: Dict[str, Any] = None):
        super().__init__(id, NodeType.TEST, properties or {})
        self.test_name = test_name
        self.file_path = file_path
        self.test_result = test_result
        
        # Update properties
        self.properties.update({
            "test_name": test_name,
            "file_path": file_path
        })
        if test_result:
            self.properties["test_result"] = test_result

def build_graph_with_tests(annotations, test_relationships):
    """
    Build a concept graph with test relationships.
    
    Args:
        annotations: List of annotations extracted from code
        test_relationships: List of test relationship objects
        
    Returns:
        The constructed concept graph
    """
    graph = ConceptGraph()
    
    # Build from annotations first
    graph.build_from_annotations(annotations)
    
    # Add test nodes and relationships
    for rel in test_relationships:
        # Create test node
        test_id = f"test:{rel.test_name}"
        test_node = TestNode(
            id=test_id,
            test_name=rel.test_name,
            file_path=rel.file_path
        )
        graph.add_node(test_node)
        
        # Find target component node
        component_id = f"component:{rel.target_component}"
        component = graph.get_node(component_id)
        
        if component:
            # Create test relationship edge
            edge = RelationshipEdge(
                source_id=test_id,
                target_id=component_id,
                edge_type=EdgeType.TESTS
            )
            graph.add_edge(edge)
            
            # If annotation reference exists, create verified_by edge
            if rel.annotation_ref:
                anno_type = rel.annotation_ref.get("type")
                anno_value = rel.annotation_ref.get("value")
                
                # Find matching annotation node
                for edge in graph.get_edges(source_id=component_id, edge_type=EdgeType.HAS_ANNOTATION):
                    anno_node = graph.get_node(edge.target_id)
                    if not anno_node:
                        continue
                    
                    if (anno_node.properties.get("annotation_type") == anno_type and
                        anno_node.properties.get("value") == anno_value):
                        # Create verified_by edge
                        verified_edge = RelationshipEdge(
                            source_id=test_id,
                            target_id=anno_node.id,
                            edge_type=EdgeType.VERIFIED_BY
                        )
                        graph.add_edge(verified_edge)
                        break
    
    return graph
```

### 5. Annotation Modification

Update annotations based on test results:

```python
class GraphUpdater:
    """Updates a concept graph based on new information."""
    
    def update_from_test_results(self, graph, test_results):
        """
        Update annotations based on test results.
        
        Args:
            graph: The concept graph to update
            test_results: Dict mapping test names to results
        
        Returns:
            Dict of updates made
        """
        updates = {
            "implementation_status_changes": [],
            "verification_status_changes": []
        }
        
        # Find test nodes
        test_nodes = [n for n in graph.nodes.values() if n.node_type == NodeType.TEST]
        
        for test_node in test_nodes:
            test_name = test_node.properties.get("test_name")
            if test_name not in test_results:
                continue
            
            # Update test result
            test_result = test_results[test_name]
            test_node.properties["test_result"] = test_result
            test_node.properties["last_run"] = datetime.now().isoformat()
            
            # Find components tested by this test
            tested_edges = graph.get_edges(source_id=test_node.id, edge_type=EdgeType.TESTS)
            
            for edge in tested_edges:
                component = graph.get_node(edge.target_id)
                if not component:
                    continue
                
                # Update verification status
                edge.properties["verification_status"] = test_result
                edge.properties["verification_date"] = datetime.now().isoformat()
                
                # Update verification_status_changes
                updates["verification_status_changes"].append({
                    "component": component.properties.get("name"),
                    "test": test_name,
                    "status": test_result
                })
                
                # If test failed, update implementation status if necessary
                if test_result == "FAILED":
                    # Find implementation status annotation
                    status_annotations = graph.query_annotations(
                        component_id=component.id,
                        annotation_type="implementation_status"
                    )
                    
                    for anno in status_annotations:
                        current_status = anno.properties.get("value")
                        if current_status in ("IMPLEMENTED", "PARTIAL"):
                            # Change to BUGGY
                            anno.properties["value"] = "BUGGY"
                            anno.properties["last_update"] = datetime.now().isoformat()
                            anno.properties["failure_reason"] = f"Test failed: {test_name}"
                            
                            updates["implementation_status_changes"].append({
                                "component": component.properties.get("name"),
                                "old_status": current_status,
                                "new_status": "BUGGY",
                                "test": test_name
                            })
        
        return updates
    
    def write_annotations_to_files(self, graph, updates):
        """
        Write updated annotations back to source files.
        
        Args:
            graph: The concept graph with updates
            updates: Dict of updates from update_from_test_results
        
        Returns:
            List of files modified
        """
        # Group updated annotations by file
        files_to_update = {}
        
        for change in updates["implementation_status_changes"]:
            component_name = change["component"]
            component_id = f"component:{component_name}"
            component = graph.get_node(component_id)
            
            if not component:
                continue
                
            file_path = component.properties.get("file_path")
            
            if not file_path:
                continue
                
            if file_path not in files_to_update:
                files_to_update[file_path] = []
                
            # Find the annotation nodes
            anno_edges = graph.get_edges(source_id=component_id, edge_type=EdgeType.HAS_ANNOTATION)
            for edge in anno_edges:
                anno = graph.get_node(edge.target_id)
                if not anno:
                    continue
                    
                if anno.properties.get("annotation_type") == "implementation_status":
                    files_to_update[file_path].append({
                        "component": component_name,
                        "line_number": anno.properties.get("line_number"),
                        "annotation_type": "implementation_status",
                        "old_value": change["old_status"],
                        "new_value": change["new_status"]
                    })
        
        # Update each file
        modified_files = []
        
        for file_path, annotations in files_to_update.items():
            if not os.path.exists(file_path):
                continue
                
            # Read file
            with open(file_path, 'r') as f:
                lines = f.readlines()
                
            # Sort annotations by line number (descending to avoid line number changes)
            annotations.sort(key=lambda a: a["line_number"], reverse=True)
            
            # Update each annotation
            modified = False
            for anno in annotations:
                line_idx = anno["line_number"] - 1
                if line_idx < 0 or line_idx >= len(lines):
                    continue
                    
                line = lines[line_idx]
                
                # Try to update the line
                if f"@implementation_status({anno['old_value']})" in line:
                    new_line = line.replace(
                        f"@implementation_status({anno['old_value']})", 
                        f"@implementation_status({anno['new_value']})"
                    )
                    lines[line_idx] = new_line
                    modified = True
                    
            # Write modified file
            if modified:
                with open(file_path, 'w') as f:
                    f.writelines(lines)
                modified_files.append(file_path)
        
        return modified_files
```

Integration with CLI:

```python
def update_command(args):
    """Update annotations based on test results."""
    test_results_file = args.test_results
    graph_file = args.graph
    output_file = args.output
    write_to_files = args.write_to_files
    
    # Load test results
    with open(test_results_file, 'r') as f:
        test_results = json.load(f)
    
    # Load graph
    graph = ConceptGraph.import_from_json(graph_file)
    
    # Update graph
    updater = GraphUpdater()
    updates = updater.update_from_test_results(graph, test_results)
    
    # Print summary
    print(f"Updated annotations:")
    print(f"- {len(updates['verification_status_changes'])} verification status changes")
    print(f"- {len(updates['implementation_status_changes'])} implementation status changes")
    
    # Write annotations to files if requested
    if write_to_files:
        modified_files = updater.write_annotations_to_files(graph, updates)
        print(f"- Modified {len(modified_files)} files")
        for file in modified_files:
            print(f"  - {file}")
    
    # Export updated graph if requested
    if output_file:
        graph.export_to_json(output_file)
        print(f"Updated graph exported to {output_file}")
    
    return 0
```

This implementation plan provides a comprehensive framework for enhancing the COP static analysis toolkit, addressing the key requirements:

1. Selective component information instead of full source code
2. A pluggable metrics system for analyzing code quality
3. Support for default annotation values
4. Test linkage analysis for connecting tests and components
5. Annotation modification based on test results

These enhancements will significantly improve the utility of the concept graph, enabling richer queries and more accurate documentation of code.

## Implementation Progress

1. ✅ Implement the selective component information extraction to reduce graph size
   - Completed extraction of selective component information (signatures, docstrings, methods, attributes)
   - Added line boundary tracking (start_line, end_line, actual_start_line)
   - Updated graph to store component_info instead of source_code
   - Verified with test module and JSONL export

## Next Steps

2. Add the metrics system for code quality analysis
3. Add support for default annotation values, starting with implementation_status
4. Integrate test relationship extraction to connect tests and components
5. Implement annotation updating based on test results

## Database Integration and Advanced Tools

Based on our exploration of DuckDB as a query engine for our exported data, we've identified several additional enhancements to improve the utility of our static analysis:

### 1. Schema Optimization for Database Queries

Improve the exported JSONL format to better support SQL and graph queries:

- Create formal schema definitions for DuckDB
- Standardize component_info format for easier query access
- Add indices for commonly queried fields
- Create predefined views for common query patterns

### 2. DuckPGQ Integration for Graph Queries

Fully leverage graph query capabilities for traversing code relationships:

- Provide helpers for creating property graphs from our exports
- Create examples of useful Cypher queries for code navigation
- Implement common graph algorithms (centrality, shortest path)
- Add documentation for graph-based code analysis patterns

### 3. Incremental Update System

Develop an efficient update mechanism to keep the database in sync with code changes:

- Create git hooks for automatic updates on commit/push
- Implement differential parsing to only process changed files
- Track component history across git commits
- Add timestamp metadata for change tracking

### 4. Code Manipulation Tools

Build higher-level tools that leverage the metadata for code modification:

- Create a symbolic function updater that uses line boundaries
- Implement annotation-aware refactoring tools
- Build an impact analysis system for proposed changes
- Develop automatic migration tools for annotation updates

These enhancements will transform our static analysis from a data extraction tool into a comprehensive code intelligence platform that supports sophisticated queries, efficient updates, and high-level code manipulation.

These changes align with the vision outlined in the COP framework documentation, particularly the concept of a living knowledge system that captures the relationships between intent, implementation, and verification.