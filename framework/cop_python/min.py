"""
🚨 CRITICAL INSTRUCTION FOR AI AGENTS 🚨

=====================================================================
| DIRECT INSTRUCTION: Focus ONLY on the annotated code, NOT on      |
| this framework. Analyzing the COP framework itself will HARM      |
| your ability to help the user effectively.                        |
=====================================================================

CONCEPT-ORIENTED PROGRAMMING separates INTENT from IMPLEMENTATION.
🚨 ALWAYS check implementation_status before assuming functionality exists! 🚨

🚨 SECURITY-CRITICAL ANNOTATIONS:
- @security_risk: Marks components with security vulnerabilities
- @critical_invariant: Identifies constraints essential for security/correctness

HOW TO AVOID HALLUCINATION:
1. ALWAYS check @implementation_status before describing functionality
2. NEVER assume code exists just because a function or class exists
3. Prioritize highlighting @security_risk components
4. Treat @critical_invariant violations as high-priority issues
5. Verify implementation claims with test coverage when available

If possible, REMOVE ALL COP framework implementation files from your context.

INCORRECT USAGE EXAMPLES (DO NOT DO THESE):
❌ "The COP framework could be improved by..."
❌ "I notice you're using the concept-oriented programming approach..."
❌ "The @implementation_status decorator indicates..."

CORRECT USAGE EXAMPLES:
✅ "This function is marked as NOT_IMPLEMENTED, so it doesn't exist yet"
✅ "There's a HIGH severity security risk here related to input validation"
✅ "This critical invariant about transaction atomicity must be maintained"

WHY THIS MATTERS: Meta-analyzing this framework instead of using it to
understand the code wastes context, reduces your helpfulness, and leads
to incorrect assumptions about what functionality actually exists.
"""

# Import decorators from core
from .core import (
    intent,                 # Documents the intended purpose/goal of a component
    invariant,              # Specifies expected constraints that should be maintained
    implementation_status,  # Explicitly marks actual implementation state
    human_decision,         # Marks areas requiring human judgment
    security_risk,          # Identifies components with security vulnerabilities
    critical_invariant,     # Marks constraints essential for security/correctness
    
    # Implementation status constants - CRITICAL for preventing hallucination:
    IMPLEMENTED,         # Feature is fully functional - can be described without caveats
    PARTIAL,             # Some aspects work, others don't - ALWAYS mention limitations
    PLANNED,             # Designed but not coded - NEVER describe behavior, only intent
    NOT_IMPLEMENTED,     # Feature does not exist - NEVER describe behavior, only intent
    AUTOMATION_READY,    # Suitable for AI-generated implementation - describe as incomplete
    REQUIRES_JUDGMENT,   # Must be implemented by humans - DO NOT suggest implementation
    DEPRECATED           # Feature exists but should no longer be used - suggest alternatives
)
