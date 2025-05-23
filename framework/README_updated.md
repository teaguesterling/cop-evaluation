# COP Testing Framework

## Overview

The Concept-Oriented Programming (COP) Framework is a Python implementation that enables explicit separation of intent from implementation, designed for effective AI-human collaboration in software development.

## Key Features

- **Annotation System**: Decorators for marking intent, implementation status, risks, invariants, and decisions
- **Runtime System**: Context management and tracing capabilities
- **Testing Integration**: Tools for testing COP-annotated code
- **Minimal Philosophy**: Testing shows that minimal annotations are more effective than comprehensive ones

## Architecture

### Core Components

1. **Runtime Layer** (`runtime.py`)
   - Context management with thread-local storage
   - System state management (enabled/disabled/tracing)
   - Source information capture for tracing

2. **Core Layer** (`core.py`)
   - Base annotation classes (`COPAnnotation`, `COPSingletonAnnotation`)
   - Annotation registration and management
   - Concept annotations for batch operations

3. **Annotations Layer** (`annotations.py`)
   - Specific annotation types:
     - `@intent` - Purpose/goal of a component
     - `@implementation_status` - Current implementation state
     - `@risk` - Security/performance concerns
     - `@invariant` - Constraints that must be maintained
     - `@decision` - Human/AI collaboration boundaries

4. **Utils Layer** (`utils.py`)
   - Helper functions for working with annotations
   - Finding components by status
   - Annotation retrieval and filtering

5. **Testing Submodule** (`testing/`)
   - Test registration and verification
   - Assertion functions for COP annotations
   - Context tracking for tests

6. **Static Analysis Toolkit** (`analysis/`)
   - AST-based annotation extraction without code execution
   - Test relationship extraction and verification tracking
   - Concept graph building with components, annotations, and tests
   - Code metrics calculation (complexity, size, dependencies)
   - JSONL export for graph database integration
   - Comprehensive CLI interface

## Implementation Status

The framework is fully functional with the following status:
- ✅ Core annotation system - IMPLEMENTED
- ✅ Runtime context management - IMPLEMENTED  
- ✅ Basic testing integration - IMPLEMENTED
- ✅ Advanced testing features - IMPLEMENTED
- ✅ Static analysis toolkit - IMPLEMENTED
- ✅ Test relationship extraction - IMPLEMENTED
- ✅ Concept graph with verification tracking - IMPLEMENTED
- ✅ CLI tools with comprehensive commands - IMPLEMENTED

## Quick Start

```python
from cop_python.annotations import (
    intent, implementation_status, risk, invariant, decision,
    IMPLEMENTED, PARTIAL, NOT_IMPLEMENTED
)

@intent("Process user payment securely")
@implementation_status(PARTIAL, details="Only credit cards supported")
@risk("Card data exposure", category="security", severity="HIGH")
def process_payment(payment_data):
    """Process payment through payment gateway."""
    # Implementation
```

## Best Practices

Based on testing results:

1. **Always use `@implementation_status`** - Critical for preventing hallucination
2. **Security annotations have highest ROI** - After implementation status
3. **Minimal is better** - Too many annotations cause "meta-distraction"
4. **Keep documentation external** - Complex invariants belong in tests, not code

## Static Analysis CLI

The framework includes a comprehensive command-line interface for static analysis:

### Basic Usage

```bash
# Extract COP annotations from code
python -m cop_python.analysis.cli extract src/ --output annotations.json

# Extract test relationships and verification status
python -m cop_python.analysis.cli test-extract tests/ --output test_relationships.json

# Build complete concept graph with annotations and tests
python -m cop_python.analysis.cli test-build src/ --test-path tests/ --output concept_graph.json

# Export to JSONL for graph database analysis
python -m cop_python.analysis.cli export src/ --output-dir graph_data/ --db concept.db
```

### Advanced Features

```bash
# Add default annotations for comprehensive coverage
python -m cop_python.analysis.cli extract src/ \
  --default-implementation-status "PROTOTYPE" \
  --default-risk "MEDIUM"

# Analyze verification coverage
python -m cop_python.analysis.cli test-build src/ --test-path tests/
# Output: 15/20 components have tests (75.0% verification coverage)
```

## Testing

The framework includes extensive tests that are now all passing:
- Runtime system tests (core functionality)
- Context management tests (thread-local storage)
- Tracing system tests (debugging features) 
- Static analysis tests (83 tests covering extraction, graph, metrics, test relationships)

To run tests:
```bash
# Run all tests
python -m pytest tests/ -v

# Run specific test suites
python -m pytest tests/test_runtime.py -v                    # Runtime tests
python -m pytest tests/test_analysis_* -v                    # Static analysis tests
```

## Examples

See `examples.py` and `test_examples.py` for comprehensive usage examples including:
- Security-critical payment processing
- AI/Human collaboration boundaries
- Module-level annotations
- Context managers for complex workflows
- Testing integration patterns

## Future Work

1. Complete the testing submodule with more examples
2. Implement CLI tools for status checking and visualization
3. Integrate with the concept graph system
4. Add more comprehensive documentation
5. Create IDE plugins for better developer experience

## Contributing

The framework follows a test-driven development approach. When contributing:
1. Add tests for new features
2. Ensure all existing tests pass
3. Follow the minimal annotation philosophy
4. Document any new annotation types

## License

MIT License - see LICENSE file for details