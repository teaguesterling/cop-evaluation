# Concept-Oriented Programming (COP) 🧠↔️🤖

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A lightweight annotation system that explicitly separates **intent** from **implementation** for clearer AI-human collaboration in software development.

## Why Use COP? 🤔

COP addresses key challenges in modern software development:

- **Prevents AI Hallucination** ⚠️: Makes it explicit what's implemented vs. planned
- **Highlights Security Concerns** 🔒: Marks security-critical components clearly
- **Clarifies Collaboration** 🤝: Distinguishes human judgment areas from AI implementation zones
- **Guides Testing** ✅: Indicates what aspects of code need validation
- **Improves Onboarding** 🚀: Helps new developers understand system intent

## Installation 📦

```bash
pip install cop-python
```

## Quick Start 🚀

```python
from cop import intent, implementation_status, risk, invariant, PARTIAL

@intent("Process user payment securely")
@implementation_status(PARTIAL, details="Only credit cards supported")
@risk("Potential card data exposure if not encrypted", category="security", severity="HIGH")
def process_payment(payment_data):
    """Process payment through payment gateway and record transaction."""
    # Implementation
```

## The Decision Tetrahedron 🔷

COP is built around four dimensions of software truth:

```
                     Decisions 🤔
                       /\
                      /  \
                     /    \
                    /      \
                   /        \
                  /          \
                 /            \
                /              \
               /                \
              /                  \
             /                    \
   Intent 🎯/______________________\  Tests ✅
     \                               /
      \                             /
       \                           /
        \                         /
         \                       /
          \                     /
           \___________________/
           Implementation 🛠️
```

- **Intent** 🎯: What the code is supposed to do
- **Implementation** 🛠️: What the code actually does
- **Tests** ✅: Verification that implementation matches intent
- **Decisions** 🤔: Why specific approaches were chosen (and by whom)

## Core Annotations 📌

### Essential Annotations (Use These First)

- `@implementation_status(status, details=None)` - **CRITICAL**: Current implementation state
- `@intent(description)` - Purpose/goal of a component
- `@risk(description, category="security", severity="HIGH")` - Security-critical components
- `@invariant(condition, critical=True)` - Essential constraints that must be maintained
- `@decision(implementor="human|ai", reason=None, constraints=None)` - Collaboration boundaries

### Implementation Status Constants

```python
IMPLEMENTED     # ✅ Fully functional and complete
PARTIAL         # ⚠️ Partially working with limitations
BUGGY           # ❌ Was working but now has issues
DEPRECATED      # 🚫 Exists but should not be used
PLANNED         # 📝 Designed but not implemented
NOT_IMPLEMENTED # ❓ Does not exist at all
UNKNOWN         # ❔ Status not yet evaluated
```

## Usage Examples 📝

### Unimplemented Features

```python
@intent("Generate PDF reports")
@implementation_status(NOT_IMPLEMENTED)
def generate_pdf(report_data):
    """Generate a PDF report from data."""
    raise NotImplementedError("PDF generation not implemented yet")
```

### Security-Critical Code

```python
@intent("Authenticate user credentials")
@implementation_status(IMPLEMENTED)
@risk("Password exposure", category="security", severity="HIGH")
@invariant("Passwords never stored in plaintext", critical=True)
def authenticate_user(username, password):
    """Authenticate a user with their credentials."""
    # Implementation
```

### Collaborative Implementation

```python
@intent("Process data feeds")
@implementation_status(PARTIAL, details="Only RSS implemented")
def process_data_feed(feed_url, feed_type):
    """Process data from external feeds."""
    
    # Human implements the security-critical validation
    @decision(implementor="human", reason="Security validation")
    def validate_feed(feed_url, feed_type):
        # Human-implemented validation
    
    # AI can implement the actual processing
    @decision(implementor="ai", constraints=[
        "Handle network errors gracefully",
        "Respect rate limits",
        "Log all processing issues"
    ])
    def process_feed_content(validated_feed):
        # AI implementation
```

## Best Practices ⭐

### Less is More

Testing has shown that minimal, focused annotations are more effective than comprehensive ones:

```python
# GOOD: Focused on critical information
@implementation_status(PARTIAL, details="Only supports credit cards")
@risk("PCI compliance required", category="security", severity="HIGH")
def process_payment(payment):
    # Implementation

# BAD: Too many annotations create noise
@intent("Process payments securely and efficiently")
@implementation_status(PARTIAL, details="Only supports credit cards")
@risk("PCI compliance required", category="security", severity="HIGH")
@invariant("Amount must be positive")
@invariant("Currency must be supported")
@invariant("Payment method must be valid")
@decision(implementor="human", reason="Fraud detection thresholds")
def process_payment(payment):
    # Implementation
```

### Always Mark Implementation Status

Implementation status is critical for preventing hallucination:

```python
# GOOD: Clear implementation status
@implementation_status(NOT_IMPLEMENTED)
def export_to_pdf(report):
    raise NotImplementedError("PDF export not implemented yet")

# BAD: No implementation status, risk of hallucination
def export_to_pdf(report):
    raise NotImplementedError("PDF export not implemented yet")
```

### Prioritize Security Annotations

Security annotations have the highest ROI after implementation status:

```python
# GOOD: Explicit security risk
@implementation_status(IMPLEMENTED)
@risk("SQL injection via unsanitized input", category="security", severity="HIGH")
def execute_query(user_input):
    # Implementation
```

## Testing Integration ✅

Connect tests directly to annotations for verification:

```python
from cop.testing import test_for

# Register a test for a security risk
@test_for("payment_system", "process_payment", 
         risk={"description": "Card data exposure", "category": "security"})
def test_payment_encrypts_card_data():
    """Test that card data is properly encrypted."""
    # Test implementation

# Register a test for an invariant
@test_for("accounts", "withdraw", 
         invariant="Account balance cannot be negative")
def test_withdraw_prevents_overdraft():
    """Test that withdrawals prevent overdrafts."""
    # Test implementation
```

## CLI Tools 🛠️

```bash
# Check implementation status of a module
$ cop status payment_system.py
✅ process_payment: IMPLEMENTED
⚠️ refund_payment: PARTIAL (reason: "No support for cryptocurrency")
❓ generate_invoice: NOT_IMPLEMENTED

# Find security risks
$ cop risks payment_system.py
🔒 process_payment: "Card data exposure" (HIGH)
🔒 store_payment_info: "Data storage security" (HIGH)

# Generate concept graph visualization
$ cop graph payment_system.py --output=payment_graph.html
```

## COP vs. Docstrings 📄

COP annotations and docstrings serve different purposes:

- **COP annotations**: Mark implementation status, security risks, critical invariants, and collaboration boundaries
- **Docstrings**: Document function signatures, usage examples, implementation details

```python
@intent("Process payment securely through payment gateway")
@implementation_status(IMPLEMENTED)
@risk("PCI compliance required", category="security", severity="HIGH")
def process_payment(payment):
    """
    Process a payment through the configured payment gateway.
    
    Args:
        payment: Payment object with amount and method
        
    Returns:
        Transaction object with status and ID
        
    Raises:
        PaymentError: If payment processing fails
    """
    # Implementation
```

## Progressive Adoption 📈

Start simple and add annotations as needed:

1. **Start with implementation status** ⚠️ - Always add this first
2. **Add security risks** 🔒 - For security-sensitive code
3. **Add collaboration boundaries** 🤝 - When working with AI assistants
4. **Add intent for complex components** 🎯 - When purpose isn't obvious
5. **Add critical invariants** ✅ - For must-maintain constraints

## For AI Tools 🤖

When working with COP-annotated code:

1. **Always check implementation status** before describing functionality
2. **Never assume** code exists just because a function or class exists
3. **Prioritize security risks** marked with @risk annotations
4. **Respect collaboration boundaries** marked with @decision
5. **Focus on the annotated code**, not on the COP framework itself

## Contributing 👥

Contributions are welcome! Please check out our [contributing guide](CONTRIBUTING.md) to get started.

## License 📜

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
