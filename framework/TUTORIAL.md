# COP Static Analysis Toolkit - Complete Tutorial

Welcome to the Concept-Oriented Programming (COP) Static Analysis Toolkit! This tutorial will walk you through all the capabilities of our toolkit using a hands-on example project.

## Overview

The COP toolkit provides comprehensive static analysis for codebases that use Concept-Oriented Programming annotations. It can:

1. **Extract COP Annotations** - Find and parse `@intent`, `@invariant`, `@risk`, `@implementation_status`, and `@decision` annotations
2. **Analyze Test Relationships** - Parse test decorators like `@test_for`, `@test_invariant` to link tests to components
3. **Build Concept Graphs** - Create rich graph representations showing relationships between components, annotations, and tests
4. **Calculate Code Metrics** - Compute complexity, size, and dependency metrics for components
5. **Export for Graph Databases** - Generate JSONL files for DuckDB/DuckPGQ analysis
6. **Track Verification Status** - Show which components have test coverage and which annotations are verified

## Prerequisites

```bash
# Ensure you have Python 3.8+ and required dependencies
pip install -r requirements.txt  # if you have one, or install manually:
# pip install pytest ast typing pathlib json
```

## Tutorial Project: E-Commerce Order System

We'll use a realistic e-commerce order processing system that demonstrates:
- Complex business logic with multiple risk levels
- Component interactions and dependencies  
- Comprehensive test coverage with various test types
- Different annotation patterns and use cases

## Part 1: Understanding the Sample Project

Let's explore our tutorial project structure:

```
examples/tutorial_ecommerce/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── order.py          # Order domain models
│   │   ├── product.py        # Product catalog models
│   │   └── user.py           # User account models
│   ├── services/
│   │   ├── __init__.py
│   │   ├── order_service.py  # Core order processing
│   │   ├── payment_service.py # Payment handling
│   │   ├── inventory_service.py # Stock management
│   │   └── notification_service.py # User notifications
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── validators.py     # Input validation utilities
│   │   └── helpers.py        # Common helper functions
│   └── main.py              # Application entry point
├── tests/
│   ├── __init__.py
│   ├── test_models.py       # Model unit tests
│   ├── test_services.py     # Service unit tests
│   ├── test_integration.py  # Integration tests
│   └── test_validators.py   # Utility tests
└── README.md               # Project documentation
```

## Part 2: COP Annotations in Practice

Our sample project uses all five COP annotation types:

### @intent - Business Purpose
```python
@intent("Process customer orders with inventory validation and payment processing")
def process_order(self, order_request: OrderRequest) -> OrderResult:
```

### @invariant - System Constraints  
```python
@invariant("total_amount > 0 and total_amount <= user.credit_limit")
def calculate_order_total(self, items: List[OrderItem]) -> Decimal:
```

### @risk - Risk Assessment
```python
@risk("HIGH", details="Handles sensitive payment data and financial transactions")
def process_payment(self, payment_info: PaymentInfo) -> PaymentResult:
```

### @implementation_status - Development State
```python
@implementation_status("IMPLEMENTED", quality="PRODUCTION_READY")
def validate_inventory(self, items: List[OrderItem]) -> ValidationResult:
```

### @decision - Architecture Choices
```python
@decision("Use Redis for inventory locking to prevent overselling", 
          alternatives=["Database locks", "Optimistic locking"])
def acquire_inventory_lock(self, product_id: str, quantity: int) -> bool:
```

## Part 3: Test Relationship Decorators

Our test suite uses specialized decorators to link tests to components:

### @test_for - Component Testing
```python
@test_for("services.order_service.OrderService.process_order")
def test_order_processing_happy_path():
```

### @test_invariant - Constraint Verification
```python
@test_invariant("total_amount > 0 and total_amount <= user.credit_limit")
def test_order_total_constraints():
```

### @test_risk - Risk Mitigation Testing
```python
@test_risk("HIGH", component="services.payment_service.PaymentService.process_payment")
def test_payment_security_measures():
```

## Part 4: Step-by-Step Analysis Walkthrough

Now let's analyze our sample project using all the toolkit capabilities:

### Step 1: Extract COP Annotations

First, let's extract all COP annotations from the source code:

```bash
# Extract annotations from the entire src/ directory
python -m cop_python.analysis.cli extract examples/tutorial_ecommerce/src/ --output tutorial_annotations.json

# View the results
python -c "
import json
with open('tutorial_annotations.json') as f:
    data = json.load(f)
    print(f'Found {len(data)} annotations across {len(set(a[\"file_path\"] for a in data))} files')
    for ann_type in ['intent', 'invariant', 'risk', 'implementation_status', 'decision']:
        count = len([a for a in data if a['annotation_type'] == ann_type])
        print(f'  {ann_type}: {count}')
"
```

### Step 2: Extract Test Relationships

Next, let's analyze the test relationships:

```bash
# Extract test relationships from test files
python -m cop_python.analysis.cli test-extract examples/tutorial_ecommerce/tests/ --output tutorial_test_relationships.json

# View the test relationship summary
python -c "
import json
with open('tutorial_test_relationships.json') as f:
    data = json.load(f)
    print(f'Found {len(data)} test relationships')
    for test_type in ['unit', 'integration', 'security', 'performance']:
        count = len([t for t in data if t['test_type'] == test_type])
        if count > 0:
            print(f'  {test_type}: {count}')
"
```

### Step 3: Build Integrated Concept Graph

Now let's build the complete concept graph with verification tracking:

```bash
# Build integrated concept graph with test relationships
python -m cop_python.analysis.cli test-build examples/tutorial_ecommerce/src/ \
  --test-path examples/tutorial_ecommerce/tests/ \
  --output tutorial_concept_graph.json

# This will show:
# - Total components found
# - Total annotations extracted  
# - Total test relationships
# - Total graph relationships
# - Test coverage statistics
```

### Step 4: Export for Graph Database Analysis

Export the data in JSONL format for advanced graph analysis:

```bash
# Export to JSONL files for DuckDB/DuckPGQ
python -m cop_python.analysis.cli export examples/tutorial_ecommerce/src/ \
  --test-path examples/tutorial_ecommerce/tests/ \
  --output-dir tutorial_graph_data/

# This creates:
# - nodes.jsonl (components, annotations, tests)
# - edges.jsonl (relationships between nodes)
# - graph_summary.json (metadata and statistics)
```

### Step 5: Analyze the Results

Let's examine what we discovered:

```bash
# View the graph summary
cat tutorial_graph_data/graph_summary.json | python -m json.tool

# Count different node types
echo "Node type distribution:"
python -c "
import json
with open('tutorial_graph_data/nodes.jsonl') as f:
    nodes = [json.loads(line) for line in f]
    
from collections import Counter
node_types = Counter(node['type'] for node in nodes)
for node_type, count in node_types.items():
    print(f'  {node_type}: {count}')
"

# Count relationship types  
echo -e "\nRelationship type distribution:"
python -c "
import json
with open('tutorial_graph_data/edges.jsonl') as f:
    edges = [json.loads(line) for line in f]
    
from collections import Counter
edge_types = Counter(edge['type'] for edge in edges)
for edge_type, count in edge_types.items():
    print(f'  {edge_type}: {count}')
"
```

## Part 5: Advanced Analysis Patterns

### Query Components by Risk Level

```bash
# Find all HIGH risk components
python -c "
import json
with open('tutorial_annotations.json') as f:
    annotations = json.load(f)

high_risk = [a for a in annotations if a['annotation_type'] == 'risk' and a['properties'].get('level') == 'HIGH']
print(f'Found {len(high_risk)} HIGH risk components:')
for ann in high_risk:
    print(f'  {ann[\"component_name\"]} ({ann[\"file_path\"]}:{ann[\"line_number\"]})')
"
```

### Check Test Coverage for Critical Components

```bash
# Find components with invariants but no tests
python -c "
import json

# Load annotations and test relationships
with open('tutorial_annotations.json') as f:
    annotations = json.load(f)
with open('tutorial_test_relationships.json') as f:
    tests = json.load(f)

# Find components with invariants
invariant_components = set(a['component_name'] for a in annotations if a['annotation_type'] == 'invariant')

# Find tested components
tested_components = set(t['target_component'] for t in tests)

# Find gaps
untested_invariants = invariant_components - tested_components
if untested_invariants:
    print(f'Components with invariants but no tests ({len(untested_invariants)}):')
    for comp in sorted(untested_invariants):
        print(f'  {comp}')
else:
    print('All components with invariants have test coverage!')
"
```

### Analyze Metrics and Complexity

```bash
# Find most complex components
python -c "
import json
with open('tutorial_concept_graph.json') as f:
    graph = json.load(f)

components = [n for n in graph['nodes'] if n['type'] == 'component']
components.sort(key=lambda x: x.get('metrics', {}).get('complexity', {}).get('cyclomatic_complexity', 0), reverse=True)

print('Most complex components:')
for comp in components[:5]:
    metrics = comp.get('metrics', {})
    complexity = metrics.get('complexity', {}).get('cyclomatic_complexity', 0)
    size = metrics.get('size', {}).get('lines_of_code', 0)
    print(f'  {comp[\"name\"]}: complexity={complexity}, loc={size}')
"
```

## Part 6: Graph Database Integration

If you have DuckDB installed, you can perform advanced graph queries:

```sql
-- Load the data into DuckDB
CREATE TABLE nodes AS SELECT * FROM read_json_auto('tutorial_graph_data/nodes.jsonl');
CREATE TABLE edges AS SELECT * FROM read_json_auto('tutorial_graph_data/edges.jsonl');

-- Find all components that implement high-risk functionality
SELECT DISTINCT c.name, c.file_path
FROM nodes c
JOIN edges e ON c.id = e.source_id  
JOIN nodes a ON e.target_id = a.id
WHERE c.type = 'component' 
  AND a.type = 'annotation'
  AND a.annotation_type = 'risk'
  AND json_extract(a.properties, '$.level') = 'HIGH';

-- Find test coverage gaps
SELECT c.name as component, COUNT(t.id) as test_count
FROM nodes c
LEFT JOIN edges e ON c.id = e.source_id AND e.type = 'tests'
LEFT JOIN nodes t ON e.target_id = t.id AND t.type = 'test'
WHERE c.type = 'component'
GROUP BY c.name
HAVING test_count = 0;
```

## Part 7: Continuous Integration Integration

You can integrate this into your CI/CD pipeline:

```bash
#!/bin/bash
# ci-cop-analysis.sh

echo "Running COP static analysis..."

# Extract annotations and check for issues
python -m cop_python.analysis.cli extract src/ --output ci_annotations.json

# Check for HIGH risk components without tests
python -m cop_python.analysis.cli test-build src/ --test-path tests/ --output ci_graph.json

# Validate that all HIGH risk components have tests
python scripts/validate_risk_coverage.py ci_annotations.json ci_graph.json

echo "COP analysis complete!"
```

## Summary

This tutorial demonstrated all major capabilities of the COP static analysis toolkit:

✅ **Annotation Extraction** - Parse COP annotations from source code  
✅ **Test Relationship Analysis** - Link tests to components and annotations  
✅ **Concept Graph Construction** - Build rich relationship graphs  
✅ **Metrics Calculation** - Analyze code complexity and quality  
✅ **Graph Database Export** - Enable advanced querying and analysis  
✅ **Verification Tracking** - Monitor test coverage and validation status

## Next Steps

1. **Apply to Your Codebase** - Use the CLI commands on your own projects
2. **Customize Annotations** - Add project-specific annotation types  
3. **Extend Metrics** - Add custom metrics providers for your analysis needs
4. **Integrate with CI/CD** - Add COP analysis to your development workflow
5. **Explore Graph Queries** - Use DuckDB/DuckPGQ for advanced analysis patterns

For more information, see the detailed documentation in `cop_python/analysis/README.md`.