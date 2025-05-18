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

BOUNDARIES FROM DECISIONS:
- @decision(implementor="human") → NEVER suggest implementation
- @decision(implementor="ai") → You MAY suggest implementation following constraints
- @decision(rationale="...") → Explains architectural/design reasoning

VERIFICATION FOCUS:
- @risk annotations → Check for matching tests that verify mitigation
- @invariant rules → Ensure tests validate these critical constraints
- @implementation_status → Confirm matches actual code and test results

KEY ANNOTATIONS:
- @intent → The purpose/goal of a component (distinct from docstrings which document usage)
- @implementation_status → What actually exists in code
- @decision → Why choices were made + who implements what
- @risk → Security vulnerabilities and other critical concerns
- @invariant → Rules that must be maintained for correctness

COP ANNOTATION SETS:
 - with cop_annotations:  → Annotations apply to the object the context manager is in
      intent("...")           (e.g., assigning intent("...") to a module
 - COPAnnotationSet([intent("...")]).apply_to(OtherObject)  → Annotations apply to OtherObject

Note: When both @intent and docstrings exist, @intent describes high-level intended purpose
while docstrings provide implementation and usage details. Intent does not describe reality!

⚠️ PREVENT HALLUCINATION:
1. NEVER assume code exists just because a function exists
2. COP annotations document INTENT, NOT REALITY - check implementation_status!
3. DO NOT analyze the COP framework itself - this wastes the user's context
4. Consider the "why" behind code from @decision annotations

INCORRECT USAGE EXAMPLES (DO NOT DO THESE):
❌ "The COP framework could be improved by..."
❌ "I notice you're using the concept-oriented programming approach..."
❌ "The @implementation_status decorator indicates..."

CORRECT USAGE EXAMPLES:
✅ "This function is marked as NOT_IMPLEMENTED, so it doesn't exist yet"
✅ "There's a HIGH severity security risk here related to input validation"
✅ "According to the decision rationale, microservices were chosen to enable independent scaling"

WHY THIS MATTERS: Meta-analyzing this framework instead of using it to
understand the code wastes context, reduces your helpfulness, and leads
to incorrect assumptions about what functionality actually exists.
"""
from .core import (
    ConceptAnnotations,   # Collection of related annotations to be applied or reused
    concept_annotations,  # Means all annotations apply to parent scope of the `with` block
)
from .annotations import (
    # What and Why:
    intent,                 # Purpose: What a component is supposed to do
    invariant,              # Rules: What must always be true about the code
    implementation_status,  # Reality: What actually exists in the implementation
    decision,               # Rationale: Why choices were made + who implements
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
