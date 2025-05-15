"""
🚨 GUIDANCE FOR WRITING COP-ANNOTATED CODE 🚨

=====================================================================
| This guide helps you WRITE code with COP annotations effectively. |
| For understanding existing code, refer to the min.py guide.       |
=====================================================================

WRITING EFFECTIVE COP ANNOTATIONS:
---------------------------------------------------------------------
💡 Annotations create bidirectional communication between humans and AI 💡

CORE PATTERNS TO FOLLOW:

1️⃣ ALWAYS mark implementation status
   @implementation_status(IMPLEMENTED)  # Complete functionality
   @implementation_status(PARTIAL, details="Only supports X")  # Be specific!
   @implementation_status(NOT_IMPLEMENTED)  # Include NotImplementedError

2️⃣ HIGHLIGHT security concerns
   @risk("SQL injection possible", severity="HIGH")  # Mark vulnerabilities
   @invariant("Inputs must be sanitized", critical=True)  # Mark requirements

3️⃣ DOCUMENT decisions and rationale
   @decision(rationale="Chose X because...")  # Explain reasoning
   @decision(implementor="human", reason="...")  # Mark human-only code
   @decision(implementor="ai", constraints=["..."])  # Provide guidance

4️⃣ CLARIFY intent
   @intent("Process payments securely")  # Express purpose clearly

PARAMETER REFERENCE:

@implementation_status(status, details=None, alternative=None)
  • status: IMPLEMENTED, PARTIAL, BUGGY, PLANNED, NOT_IMPLEMENTED, UNKNOWN, DEPRECATED
  • details: Explain limitations or partial implementation
  • alternative: For DEPRECATED, what to use instead

@risk(description, severity="MEDIUM")
  • description: What the risk is
  • severity: "LOW", "MEDIUM", "HIGH", "CRITICAL"

@invariant(condition, critical=False)
  • condition: What must always be true
  • critical: Whether essential for security/correctness

@decision(description=None, implementor=None, constraints=None, rationale=None, 
         options=None, answer=None, decider=None)
  • description: Decision question/description
  • implementor: Who should implement ("human", "ai", etc.)
  • constraints: Requirements for implementation
  • rationale: Why this decision was made
  • options: Considered alternatives
  • answer: The selected option
  • decider: Who made the decision

@intent(description)
  • description: Purpose of the component

EXAMPLE: EFFECTIVE ANNOTATION PATTERNS

# Security-critical component
@intent("Authenticate users securely")
@implementation_status(IMPLEMENTED)
@risk("Credential exposure", severity="HIGH")
@invariant("Passwords never stored in plaintext", critical=True)
@decision("Use bcrypt for hashing", rationale="Industry standard with work factor")
def authenticate_user(username, password):
    # Implementation...

# AI-implementable component
@intent("Validate email format")
@implementation_status(NOT_IMPLEMENTED)
@decision(
    implementor="ai",
    constraints=["RFC 5322 compliant", "Handle Unicode domains"]
)
def validate_email(email):
    # Implementation needed

# Component with known limitations
@intent("Process payment transactions")
@implementation_status(PARTIAL, details="Credit cards only, no cryptocurrency")
@risk("PCI compliance required", severity="HIGH")
@invariant("Transactions must be atomic", critical=True)
def process_payment(payment_info):
    # Implementation...
"""

from .core import (
    # Core annotations:
    intent,                 # Purpose: Document component goals
    implementation_status,  # Reality: Mark what actually exists
    decision,               # Why/Who: Explain reasoning and ownership
    risk,                   # Concerns: Highlight security issues
    invariant,              # Rules: Specify critical constraints
    
    # Implementation states:
    IMPLEMENTED,         # ✅ Fully functional and complete
    PARTIAL,             # ⚠️ Partially working with limitations
    BUGGY,               # ❌ Was working but now has issues
    DEPRECATED,          # 🚫 Exists but should not be used
    PLANNED,             # 📝 Designed but not implemented
    NOT_IMPLEMENTED,     # ❓ Does not exist at all
    UNKNOWN,             # ❔ Status not yet evaluated
)

# More detailed examples are available if needed
# This file focuses on the core patterns for effective annotation
