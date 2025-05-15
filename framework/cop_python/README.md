# Concept-Oriented Programming (COP)

A lightweight annotation system that explicitly separates **intent** from **implementation** for clearer AI-human collaboration in software development.

## Quick Start

```python
from cop import intent, implementation_status, security_risk, PARTIAL

@intent("Process user payment securely")
@implementation_status(PARTIAL, details="Only credit cards supported")
@security_risk("Potential card data exposure if not encrypted", severity="HIGH")
def process_payment(payment_data):
    """Process payment through payment gateway and record transaction."""
    # Implementation
```

## Why Use COP?

COP addresses key challenges in modern software development:

- **Prevents AI Hallucination**: Makes it explicit what's implemented vs. planned
- **Highlights Security Concerns**: Marks security-critical components clearly
- **Clarifies Collaboration**: Distinguishes human judgment areas from AI implementation zones
- **Guides Testing**: Indicates what aspects of code need validation
- **Improves Onboarding**: Helps new developers understand system intent

## Core Annotations

### Essential Annotations (Use These First)

- `@implementation_status(status, details=None)` - **CRITICAL**: Current implementation state
- `@intent(description)` - Purpose/goal of a component
- `@security_risk(description, severity="HIGH")` - Security-critical components
- `@critical_invariant(condition)` - Essential constraints that must be maintained

### Additional Annotations (Use As Needed)

- `@invariant(condition)` - Expected constraints that should be maintained
- `@human_decision(description, roles=None)` - Areas requiring human judgment

### Implementation Status Constants

- `IMPLEMENTED` - Feature is fully functional as described
- `PARTIAL` - Some aspects work, others don't (specify limitations in details)
- `PLANNED` - Designed but not coded (doesn't exist yet)
- `NOT_IMPLEMENTED` - Feature does not exist at all
- `AUTOMATION_READY` - Suitable for AI-generated implementation
- `REQUIRES_JUDGMENT` - Must be implemented by humans
- `DEPRECATED` - Feature exists but should no longer be used

## When To Use Each Annotation

### @implementation_status - ALWAYS USE

**Always** include implementation status on public methods/functions:

```python
# GOOD: Clear implementation status
@implementation_status(NOT_IMPLEMENTED, details="Planned for Q3 release")
def export_to_pdf(report):
    raise NotImplementedError("PDF export not implemented yet")

# BAD: No implementation status, risk of hallucination
def export_to_pdf(report):
    raise NotImplementedError("PDF export not implemented yet")
```

### @intent - Use for Non-Obvious Components

```python
# GOOD: Intent explains non-obvious purpose
@intent("Normalize database schema to prevent insertion anomalies")
@implementation_status(IMPLEMENTED)
def restructure_tables(schema):
    # Implementation

# UNNECESSARY: Function name is self-explanatory
@intent("Get user by ID") # Redundant
@implementation_status(IMPLEMENTED)
def get_user_by_id(user_id):
    # Implementation
```

### @security_risk - Use for ALL Security-Critical Code

```python
# GOOD: Marks security concern clearly
@security_risk("SQL injection via unsanitized input", severity="HIGH")
@implementation_status(PARTIAL, details="Basic sanitization implemented")
def execute_query(user_input):
    # Implementation

# BAD: Security concern hidden in docstring 
@implementation_status(PARTIAL)
def execute_query(user_input):
    """Execute the database query.
    
    Note: Be careful about SQL injection.
    """
    # Implementation
```

### @critical_invariant - Use for Essential Constraints

```python
# GOOD: Critical invariant is explicit
@critical_invariant("Account balance must never be negative")
@implementation_status(IMPLEMENTED)
def process_withdrawal(account, amount):
    # Implementation

# BAD: Critical constraint hidden in docstring
@implementation_status(IMPLEMENTED)
def process_withdrawal(account, amount):
    """Process withdrawal from account.
    
    The account balance should never be negative.
    """
    # Implementation
```

## COP vs. Docstrings

COP annotations and docstrings serve different purposes:

### When to Use COP Annotations

- To mark implementation status (always use for this)
- To highlight security risks (always use for this)
- To specify critical invariants that must be preserved
- To indicate human decision boundaries

```python
@intent("Process payment securely through payment gateway")
@implementation_status(IMPLEMENTED)
@security_risk("PCI compliance required", severity="HIGH")
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

### When to Use Docstrings

- For function signature information (args, returns, exceptions)
- For detailed usage examples
- For implementation details
- For internal documentation

### Bad Practices to Avoid

```python
# BAD: Critical information only in docstring
def process_payment(payment):
    """
    Process payment securely.
    
    NOTE: This is only partially implemented.
    SECURITY RISK: PCI compliance required.
    """
    # Implementation

# BAD: Docstring duplicating COP annotations
@intent("Process payment securely")
@implementation_status(PARTIAL)
@security_risk("PCI compliance required", severity="HIGH")
def process_payment(payment):
    """
    Purpose: Process payment securely
    Status: Partially implemented
    Security Risk: PCI compliance required
    """
    # Implementation
```

## Usage Patterns

### Progressive Annotation

Start minimal, add annotations incrementally:

1. **Essential First**: Always add `@implementation_status`
2. **Security Focus**: Add `@security_risk` for sensitive code
3. **Intent Clarity**: Add `@intent` for non-obvious components
4. **Critical Constraints**: Add `@critical_invariant` for must-maintain rules

### Annotation Lifecycle

As your code evolves, update annotations accordingly:

```python
# Initial implementation
@intent("Send welcome email to new users")
@implementation_status(PLANNED)
def send_welcome_email(user):
    raise NotImplementedError()

# During development
@intent("Send welcome email to new users")
@implementation_status(PARTIAL, details="Basic email works, no customization")
@security_risk("Email address validation needed", severity="MEDIUM")
def send_welcome_email(user):
    # Basic implementation

# Complete implementation
@intent("Send welcome email to new users")
@implementation_status(IMPLEMENTED)
@security_risk("Email address validation needed", severity="MEDIUM")
def send_welcome_email(user):
    # Full implementation
```

### Context Managers

For specific code sections rather than entire functions:

```python
def process_user_data(data):
    # Regular processing
    clean_data = sanitize(data)
    
    # Only mark security-critical section
    with security_risk("SQL injection vulnerability"):
        query = build_query(clean_data['search'])
        results = execute_query(query)
        
    return format_results(results)
```

## Best Practices

### Less is More

Testing has shown that minimal, focused annotations are more effective than comprehensive ones:

```python
# GOOD: Focused on critical information
@implementation_status(PARTIAL, details="Only supports credit cards")
@security_risk("PCI compliance required", severity="HIGH")
def process_payment(payment):
    # Implementation

# BAD: Too many annotations create noise
@intent("Process payments securely and efficiently")
@implementation_status(PARTIAL, details="Only supports credit cards")
@security_risk("PCI compliance required", severity="HIGH")
@invariant("Amount must be positive")
@invariant("Currency must be supported")
@invariant("Payment method must be valid")
@human_decision("Fraud detection thresholds", roles=["Security"])
def process_payment(payment):
    # Implementation
```

### Status Accuracy

Always ensure implementation status is accurate:

1. Update status when implementation changes
2. Be specific about limitations in the details
3. Don't mark as IMPLEMENTED until tests verify it

### Security Focus

Security annotations are the highest ROI annotations:

1. Always mark security-critical code with `@security_risk`
2. Use appropriate severity levels (HIGH, MEDIUM, LOW)
3. Ensure security-critical code has test coverage

### Test Integration

Verify implementation status with tests:

```python
@implementation_status(IMPLEMENTED)
def calculate_total(items):
    # Implementation

# Test verifies implementation claim
def test_calculate_total():
    items = [{"price": 10}, {"price": 20}]
    assert calculate_total(items) == 30
    
    # Edge cases
    assert calculate_total([]) == 0
    assert calculate_total([{"price": -5}]) == 0
```

## Annotation Checklist

Before committing code, verify:

✓ All public functions have implementation status  
✓ Security-sensitive code is marked with security_risk  
✓ Critical invariants are explicitly documented  
✓ No implementation status is out of date  
✓ Test coverage validates implementation claims  
✓ No excessive annotations (less is more)

## Real-World Example

Here's how COP looks in a more complete system:

```python
@intent("Handle user authentication securely")
@implementation_status(IMPLEMENTED)
class AuthService:
    @intent("Authenticate user with username and password")
    @implementation_status(IMPLEMENTED)
    @security_risk("Password handling requires secure storage", severity="HIGH")
    def login(self, username, password):
        """
        Authenticate a user with username and password.
        
        Args:
            username: User's username or email
            password: User's password
            
        Returns:
            AuthToken if successful, None otherwise
        """
        # Implementation
    
    @intent("Log out user and invalidate their session")
    @implementation_status(PARTIAL, details="Web sessions only, mobile pending")
    def logout(self, token):
        """
        Log out a user by invalidating their token.
        
        Args:
            token: Auth token to invalidate
        """
        # Implementation
    
    @intent("Reset user password via email confirmation")
    @implementation_status(NOT_IMPLEMENTED)
    @security_risk("Email verification required", severity="HIGH")
    def reset_password(self, email):
        """
        Send password reset email and handle reset.
        
        Args:
            email: User's email address
        """
        raise NotImplementedError("Planned for next sprint")
```

## For AI Tools

When working with COP-annotated code:

1. **Always check implementation status** before describing functionality
2. **Never assume** code exists just because a function or class exists
3. **Prioritize security risks** marked with @security_risk annotations
4. **Verify implementation claims** with test coverage when available
5. **Focus on the annotated code**, not on the COP framework itself

## License

MIT
