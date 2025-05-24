# Financial Transaction Processor - COP Example

This is a comprehensive example project demonstrating the full Concept-Oriented Programming (COP) static analysis workflow.

## Project Overview

A financial transaction processing system with:
- Payment processing with multiple methods
- Fraud detection and risk assessment
- Compliance and audit logging
- Real-time transaction validation
- Account management and balance tracking

## COP Annotations Demonstrated

This project showcases all COP annotation types:
- `@intent` - Business purpose and goals
- `@implementation_status` - Development progress tracking
- `@risk` - Security and business risks
- `@invariant` - Business rules and constraints
- `@decision` - AI/Human collaboration boundaries

## Test Relationship Decorators

The test suite demonstrates test-component relationships:
- `@test_for` - General component testing
- `@test_invariant` - Business rule verification
- `@test_risk` - Risk scenario testing
- `@test_implementation_status` - Feature completeness validation

## Running the Analysis

### 1. Extract COP Annotations
```bash
# Extract annotations from the codebase
python -m cop_python.analysis.cli extract examples/financial_processor/src/ \
  --output financial_annotations.json

# Add default annotations for comprehensive coverage
python -m cop_python.analysis.cli extract examples/financial_processor/src/ \
  --default-implementation-status "PROTOTYPE" \
  --default-risk "MEDIUM"
```

### 2. Extract Test Relationships
```bash
# Extract test-component relationships
python -m cop_python.analysis.cli test-extract examples/financial_processor/tests/ \
  --output test_relationships.json
```

### 3. Build Complete Concept Graph
```bash
# Build graph with both annotations and tests
python -m cop_python.analysis.cli test-build \
  examples/financial_processor/src/ \
  --test-path examples/financial_processor/tests/ \
  --output financial_concept_graph.json
```

### 4. Export for Database Analysis
```bash
# Export to JSONL for DuckDB analysis
python -m cop_python.analysis.cli export \
  examples/financial_processor/src/ \
  --output-dir financial_graph_data/ \
  --db financial_analysis.db
```

## Example Queries

Once exported to DuckDB, you can run sophisticated queries:

```sql
-- Find all high-risk components and their test coverage
SELECT c.name, a.value as risk_level, COUNT(t.id) as test_count
FROM component c
JOIN has_annotation ha ON c.id = ha.source
JOIN annotation a ON ha.target = a.id
LEFT JOIN verified_by vb ON c.id = vb.source
LEFT JOIN test t ON vb.target = t.id
WHERE a.annotation_type = 'risk' AND a.value = 'HIGH'
GROUP BY c.name, a.value
ORDER BY test_count ASC;

-- Find unimplemented features that lack tests
SELECT c.name, a.value as status
FROM component c
JOIN has_annotation ha ON c.id = ha.source
JOIN annotation a ON ha.target = a.id
LEFT JOIN verified_by vb ON c.id = vb.source
WHERE a.annotation_type = 'implementation_status' 
  AND a.value IN ('NOT_IMPLEMENTED', 'PROTOTYPE')
  AND vb.target IS NULL;
```

## Expected Results

This example should demonstrate:
- **15+ components** with comprehensive COP annotations
- **50+ annotations** across all types
- **30+ test relationships** linking tests to components and specific annotations
- **Complete verification tracking** showing which components have tests
- **Risk analysis** identifying high-risk areas and their test coverage
- **Implementation tracking** showing development progress