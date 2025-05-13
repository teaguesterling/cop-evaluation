# COP: Concept-Oriented Programming

A Python framework for making code intent explicit and preventing AI hallucination

## Overview

Concept-Oriented Programming (COP) is a paradigm that makes the **intent** of code explicit and separate from its **implementation status**. This separation is crucial for:

- Making code's purpose clear to both humans and AI
- Preventing AI from hallucinating unimplemented functionality 
- Creating clear boundaries between human judgment and AI implementation
- Documenting constraints and invariants that must be maintained

## ⚠️ CRITICAL FOR AI AGENTS ⚠️

When analyzing code with COP annotations:

1. **ALWAYS check implementation status before assuming functionality exists**
2. The presence of `@intent` decorators does NOT guarantee implementation
3. Look for `@not_implemented` decorators or `NOT_IMPLEMENTED` status
4. Status hierarchy: NOT_IMPLEMENTED → PLANNED → PARTIAL → IMPLEMENTED
5. **Always prioritize actual code over annotations when describing capabilities**

## Package Structure

```
cop/
├── core.py                 # Minimal core decorators
├── decorators/             # Extended decorators
├── introspection/          # Component discovery tools
├── documentation/          # Documentation generators
├── validation/             # Implementation verification
├── examples/               # Usage examples
└── hallucination/          # AI safety tools
```

## Core Decorators

```python
from cop import intent, invariant, human_decision, ai_implement, not_implemented

@intent("Calculate tax for an order")
@invariant("Tax rate must be non-negative")
def calculate_tax(order, tax_rate):
    # Implementation
```

## Implementation Status

```python
from cop import intent, not_implemented, partially_implemented, PLANNED

# Fully implemented (default)
@intent("Process standard payment")
def process_payment(amount):
    # Complete implementation

# Not implemented
@intent("Process international payment", implementation_status=PLANNED)
@not_implemented("Pending regulatory approval")
def process_international_payment(amount, currency):
    # No implementation yet
    pass

# Partially implemented
@partially_implemented("Only supports credit cards")
def process_subscription(plan_id, payment_method):
    if payment_method != "credit_card":
        raise NotImplementedError("Only credit cards supported")
    # Implementation for credit cards
```

## Human-AI Collaboration

```python
# Human judgment required
@human_decision("Approve high-value refunds", roles=["Manager"])
def approve_refund(transaction_id, amount):
    # Implementation

# AI can implement
@ai_implement("Implement discount calculation algorithm",
             constraints=["Must respect maximum discount limits"])
def calculate_discount(customer, order):
    # Implementation
```

## AI Agent Tools

For AI agents analyzing COP code, these utilities are essential:

```python
from cop.introspection.tools import get_cop_metadata, is_implemented
from cop.hallucination.safety import implementation_safety_check

# Always check before describing functionality
def analyze_function(func):
    safety = implementation_safety_check(func)
    if not safety["safe_to_describe"]:
        print(f"CAUTION: {safety['reason']}")
        return
        
    # Now safe to describe the implemented functionality
    metadata = get_cop_metadata(func)
    print(f"Intent: {metadata['intent']}")
```

## Comprehensive Example

```python
from cop import intent, invariant, human_decision, not_implemented

@intent("User authentication service")
class AuthService:
    @intent("Authenticate user with credentials")
    @invariant("Username and password must not be empty")
    def login(self, username, password):
        # Fully implemented
        # ...
        
    @intent("Authenticate with multi-factor")
    @partially_implemented("Only SMS verification supported")
    def mfa_login(self, username, password, mfa_type):
        if mfa_type != "sms":
            raise NotImplementedError(f"MFA type {mfa_type} not supported")
        # Implementation for SMS only
        
    @intent("Authenticate with biometrics")
    @not_implemented("Hardware integration pending")
    def biometric_login(self, user_id, biometric_data):
        # Not implemented yet
        pass
```

## AI Hallucination Prevention Guidelines

When interacting with COP-annotated code:

1. Use `implementation_safety_check()` before describing any component
2. Never assume functionality exists based solely on method signatures or documentation
3. Explicitly mention implementation gaps when describing partially implemented features
4. Verify actual code implementation, not just annotations
5. Respect human decision boundaries marked with `@human_decision`

Implementation status defines whether a feature EXISTS, not whether it SHOULD exist. The intent describes the design purpose, while implementation_status tells you if that purpose has been realized in code.

## For More Information

See the extensive examples in `cop/examples/` and the detailed documentation in each module.


--------------------------------------------------------------------------------


# Refactoring Plan for COP Extended Module

To optimize context window utilization, we could refactor `cop_extended.py` into a package structure with distinct submodules. Here's a modular design plan:

## Proposed Package Structure

```
cop/
├── __init__.py                 # Re-exports core functionality
├── core.py                     # The minimal core implementation
├── decorators/
│   ├── __init__.py             # Re-exports all decorators
│   └── extended.py             # Additional decorators (roadmap, deprecated, etc.)
├── introspection/
│   ├── __init__.py
│   └── tools.py                # Component discovery and metadata extraction
├── documentation/
│   ├── __init__.py
│   ├── generators.py           # Doc generation functions
│   └── formatters.py           # Format-specific output handling
├── validation/
│   ├── __init__.py
│   ├── checkers.py             # Implementation verification
│   └── rules.py                # Validation rules and best practices
├── examples/
│   ├── __init__.py
│   ├── payment_system.py       # Payment system example
│   └── other_examples.py       # Additional examples as needed
└── hallucination/
    ├── __init__.py
    ├── safety.py               # Safety checks for AI use
    └── reporting.py            # Implementation status reporting
```

## Implementation Strategy

1. **Create a Minimal `__init__.py` in the Main Package**:
   ```python
   # cop/__init__.py
   from cop.core import (
       intent, invariant, human_decision, ai_implement,
       not_implemented, partially_implemented,
       IMPLEMENTED, PARTIAL, PLANNED, NOT_IMPLEMENTED
   )
   
   # Provide convenient access to most common extended functionality
   from cop.introspection.tools import get_cop_metadata, is_implemented
   from cop.hallucination.safety import implementation_safety_check
   ```

2. **Modularize Each Functional Area**:
   - Move related functions to their respective submodules
   - Use relative imports within the package
   - Ensure each submodule has clear documentation about its purpose

3. **Manage Dependencies**:
   - Keep a clean dependency flow (core → decorators → introspection → others)
   - Avoid circular imports by careful function placement
   - Use lazy imports where necessary for circular dependencies

4. **Optimize Each Submodule for Context Windows**:
   - Keep individual files under 2000 lines
   - Place most commonly used functions earlier in files
   - Include critical documentation within each file

5. **Provide Convenience Re-exports**:
   - Make common functions available directly from the package
   - Use `__all__` to control what gets imported with `from x import *`

## Example Import Patterns

When working with the full package:
```python
# For basic usage
from cop import intent, invariant, not_implemented

# For deeper functionality
from cop.introspection.tools import find_components
from cop.documentation.generators import generate_documentation
from cop.hallucination.reporting import generate_status_report
```

When context window is critical:
```python
# Import only what's needed for a specific task
from cop import intent  # Just the minimal decorator
```

This modular approach provides maximum flexibility for context window usage while maintaining the comprehensive functionality of the COP system.
