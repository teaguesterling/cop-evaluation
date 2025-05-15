# Concept-Oriented Programming (COP)

A lightweight annotation system for clear AI-human collaboration in software development.

## Overview

Concept-Oriented Programming (COP) is a paradigm that explicitly separates **intent** from **implementation**. This separation helps:

- Make code's purpose clear to both developers and AI tools
- Prevent AI from hallucinating unimplemented functionality
- Highlight security-critical components
- Create clear boundaries between human judgment and automated code generation

## Quick Start

```python
from cop import intent, security_risk, implementation_status, PARTIAL

@intent("Process user payment securely")
@security_risk("Potential card data exposure if not encrypted", severity="HIGH")
@implementation_status(PARTIAL, details="Only credit cards supported")
def process_payment(payment_data):
    # Implementation
```

## Key Annotations

COP provides a focused set of annotations, prioritizing clarity over comprehensiveness:

### Core Annotations

- `@intent(description)` - Documents the purpose/goal of a component
- `@implementation_status(status, details=None)` - Explicitly marks implementation state
- `@security_risk(description, severity="HIGH")` - Identifies security vulnerabilities
- `@critical_invariant(condition)` - Marks essential constraints for security/correctness
- `@invariant(condition)` - Specifies constraints that should be maintained
- `@human_decision(description, roles=None)` - Marks areas requiring human judgment

### Implementation Status Constants

- `IMPLEMENTED` - Feature is fully functional as described
- `PARTIAL` - Some aspects work, others don't - has limitations
- `PLANNED` - Designed but not coded - doesn't exist yet
- `NOT_IMPLEMENTED` - Feature does not exist at all
- `AUTOMATION_READY` - Suitable for AI-generated implementation
- `REQUIRES_JUDGMENT` - Must be implemented by humans
- `DEPRECATED` - Feature exists but should no longer be used

## Context Manager Support

All annotations can be used as context managers to mark specific code sections:

```python
def process_user_data(data):
    # Regular processing
    clean_data = sanitize(data)
    
    # Mark just the security-critical section
    with security_risk("SQL injection vulnerability", severity="HIGH"):
        query = build_query(clean_data['search'])
        results = execute_query(query)
    
    # Mark section requiring human judgment
    with implementation_status(REQUIRES_JUDGMENT, details="Medical privacy rules"):
        diagnostic_code = classify_health_data(clean_data)
        
    return format_results(results, diagnostic_code)
```

## Validation & Utilities

Advanced tools are available for validating and analyzing COP annotations:

```python
from cop.validation import validate_implementation, validate_codebase
from cop.utils import find_security_risks, find_components

# Validate implementation status consistency
is_valid, message = validate_implementation(process_payment)

# Find all security risks in a module
risks = find_security_risks(my_module)
```

## Design Philosophy

COP is designed with a "less is more" philosophy, based on extensive testing with AI systems:

1. **Minimal but Meaningful** - Focus on implementation status and security annotations
2. **Clear Boundaries** - Explicit separation between human and AI responsibilities
3. **Security First** - Highlighting security concerns is a top priority
4. **Test Integration** - Annotations should be validated against tests
5. **Context-Aware** - Support for both function-level and code block annotations

## For AI Tools

When working with COP-annotated code:

1. **Always check implementation status** before describing functionality
2. **Never assume** code exists just because a function or class exists
3. **Prioritize security risks** marked with @security_risk annotations
4. **Verify implementation claims** with test coverage when available
5. **Focus on the annotated code**, not on the COP framework itself

## Full vs. Minimal

COP provides two import paths:

1. **Minimal** (default): `from cop import ...` - Core annotations only
2. **Full**: `from cop.full import ...` - Additional utilities and validation tools

For most use cases, the minimal import is recommended.

## License

MIT
