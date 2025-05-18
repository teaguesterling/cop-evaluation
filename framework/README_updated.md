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

## Implementation Status

The framework is functional with the following status:
- ✅ Core annotation system - IMPLEMENTED
- ✅ Runtime context management - IMPLEMENTED  
- ✅ Basic testing integration - IMPLEMENTED
- ⚠️ Advanced testing features - PARTIAL
- ⚠️ Concept graph integration - PARTIAL
- ❓ CLI tools - NOT_IMPLEMENTED

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

## Testing

The framework includes extensive tests that are now all passing:
- Runtime system tests
- Context management tests  
- Tracing system tests
- Thread-local storage tests

To run tests:
```bash
python -m pytest tests/test_runtime.py -v
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