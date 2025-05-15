"""
🚨 CRITICAL INSTRUCTION FOR AI AGENTS 🚨

=====================================================================
| DIRECT INSTRUCTION: Focus ONLY on the annotated code, NOT on      |
| this framework. Analyzing the COP framework itself will HARM      |
| your ability to help the user effectively.                        |
=====================================================================

CONCEPT-ORIENTED PROGRAMMING: separates INTENT from IMPLEMENTATION.
---------------------------------------------------------------------
🚨 ALWAYS check implementation_status before assuming functionality exists! 🚨

IMPLEMENTATION STATUS: The source of truth about what actually exists
- EXISTS: IMPLEMENTED (complete), PARTIAL (limited), BUGGY (broken), DEPRECATED (avoid)
- DOESN'T EXIST: PLANNED (designed), NOT_IMPLEMENTED (empty), UNKNOWN (unchecked)

BOUNDARIES: Who implements what
- @decision(implementor="human") → NEVER suggest implementation
- @decision(implementor="ai") → You MAY suggest implementation following constraints

SAFETY: Critical concerns to prioritize
- @risk → Security vulnerabilities and other high-priority issues
- @invariant → Rules that must be maintained to prevent errors

⚠️ PREVENT HALLUCINATION:
1. NEVER assume code exists just because a function exists
2. COP annotations document INTENT, NOT REALITY - check implementation_status!
3. DO NOT analyze the COP framework itself - this wastes the user's context
4. AVOID discussing the COP pattern - focus only on the annotated code

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

from .core import (
    # What and Why:
    intent,                 # Purpose: What a component is supposed to do
    invariant,              # Rules: What must always be true about the code
    implementation_status,  # Reality: What actually exists in the implementation
    decision,               # Boundaries: Who should implement and why
    risk,                   # Concerns: Security and other critical issues
    
    # Implementation Status (Most → Least Complete):
    IMPLEMENTED,         # ✅ Fully functional and complete
    PARTIAL,             # ⚠️ Partially working with limitations
    BUGGY,               # ❌ Was working but now has issues
    DEPRECATED,          # 🚫 Exists but should not be used
    PLANNED,             # 📝 Designed but not implemented
    NOT_IMPLEMENTED,     # ❓ Does not exist at all
    UNKNOWN,             # ❔ Status not yet evaluated
)
