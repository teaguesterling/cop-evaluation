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
  • details: Optionally, explain limitations or partial implementation
  • alternative: For DEPRECATED, what to use instead

@risk(description, category="security", severity="MEDIUM", impact=None, mitigation=None)
  • description: What the risk is
  • category: The risk categury: ("security", "performance", etc.)
  • severity: "LOW", "MEDIUM", "HIGH", "CRITICAL"
  • impact: An optional assessement of the impact of the risk if not addressed
  • mitigation: An optional list of any mitigation strategies that *have been* taken

@invariant(condition, critical=False, scope="always")
  • condition: What must always be true
  • critical: Whether essential for security/correctness
  • scope: What's the scope of this invariant (should be ommitted if "always")

@decision(description=None, implementor=None, constraints=None, rationale=None, 
         options=None, answer=None, decider=None, **kwargs)
(All arguments here are optional and should only be included if explicitly relevant)
  • description: Decision question/description
  • implementor: Who should implement ("human", "ai", etc.)
  • constraints: Requirements for implementation
  • rationale: Why this decision was made
  • options: Considered alternatives
  • answer: The selected option
  • decider: Who made the decision
  • **kwargs: Other annotations are captured and preserved

@intent(description)
  • description: Purpose of the component

TESTING ANNOTATIONS:
Tests complete the truth triangle by verifying that implementation matches intent.
- Write tests that explicitly verify @invariant conditions
- Ensure @risk annotations have matching security tests
- Use test results to validate @implementation_status claims
- Remember: Untested invariants are just aspirations

THE DECISION TETRAHEDRON:
COP connects four dimensions of software understanding:
- Intent: What we want to accomplish
- Implementation: What actually exists in code
- Tests: Verification that code works correctly
- Decisions: Why we chose specific approaches
  
Capturing decisions creates a complete picture that preserves
knowledge that would otherwise be lost over time.

ANNOTATION BALANCE:
"Less is more" - Focus on quality over quantity
- ALWAYS include implementation status
- Add security risks and critical invariants
- Document important decisions, not trivial ones
- Limit to 3-4 annotations per component
- Annotate public interfaces more thoroughly than internals

DOCUMENTATION BEST PRACTICES:
Deciding when to use @intent, docstrings, or both together:

DOCSTRINGS ALONE: For implementation-focused documentation
- When function names are self-explanatory
- For internal implementation details
- When parameter documentation is the primary focus
- Example:
  def format_date(date, format_string="%Y-%m-%d"):
      """
      Format a date according to the specified format string.
      
      Args:
          date: The date to format
          format_string: strftime-compatible format string
      """

@INTENT ALONE: For concept-level documentation
- When tracking purpose separate from implementation
- When paired with implementation status tracking
- For architectural/conceptual organization
- Example:
  @intent("Calculate risk score per regulatory requirements")
  @implementation_status(PARTIAL, details="Missing PEP check")
  def calculate_risk_score(transaction):
      # Implementation with simple parameters

COMBINED APPROACH: For complete documentation
- Security-critical components needing both intent and usage clarity
- Complex domain concepts with significant technical details
- Public APIs with implementation status concerns
- Example:
  @intent("Execute batch transaction processing")
  @implementation_status(PARTIAL, details="No rollback support")
  def process_batch(transactions):
      """
      Process multiple transactions as a batch.
      
      Args:
          transactions: List of Transaction objects
      """

RULE OF THUMB:
- Use @intent when the concept matters for architectural understanding
- Use docstrings when usage details matter for developers calling the function
- Use both when both conceptual understanding and usage details are important
- Default to docstrings and add @intent only when concept-oriented benefits are clear

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


   TESTING COP ANNOTATIONS:
---------------------------------------------------------------------
Tests complete the truth triangle by verifying implementation matches intent.

1️⃣ LINK TESTS TO COMPONENTS:
   @intent.test_for(process_payment, "Process payments securely")
   def test_payment_intent():
       # Test that verifies the implementation fulfills the intent

2️⃣ VERIFY IMPLEMENTATION STATUS:
   @implementation_status.test_for(process_payment, IMPLEMENTED)
   def test_implementation_completeness():
       assert_implementation_matches_status(process_payment, True)

3️⃣ TEST INVARIANTS:
   @invariant.test_for(process_payment, "Transactions must be atomic")
   def test_transaction_atomicity():
       # Test that verifies this invariant is maintained

4️⃣ VERIFY SECURITY RISKS:
   @risk.test_for(process_payment, "Card data exposure")
   def test_card_data_security():
       assert_security_requirement(is_data_encrypted(payment_data))

5️⃣ EXTERNALIZED INVARIANTS: For detailed invariants without cluttering code
   # In core code - keep minimal
   @invariant("See test file for detailed invariants")
   def process_payment():
       # Implementation
   
   # In test file - define detailed invariants
   @register_invariants("payment_system.process_payment")
   class PaymentInvariants:
       currency_must_be_supported = "Currency must be supported"
       amount_must_be_positive = "Amount must be positive"
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
