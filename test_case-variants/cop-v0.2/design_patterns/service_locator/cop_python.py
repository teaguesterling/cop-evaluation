"""
CONCEPT-ORIENTED PROGRAMMING (COP) CORE

⚠️ CRITICAL WARNING: COP annotations document INTENT, NOT REALITY ⚠️

FUNDAMENTAL PRINCIPLE: COP separates what code is DESIGNED to do from what
it ACTUALLY does. This distinction is essential to prevent hallucination.

IMPLEMENTATION STATUS HIERARCHY:
- NOT_IMPLEMENTED: Feature doesn't exist at all
- PLANNED: Designed but no implementation
- PARTIAL: Some aspects implemented, others missing  
- IMPLEMENTED: Fully functional as described

ALWAYS check implementation_status before assuming functionality exists!

Example:
  status = getattr(obj, "__cop_implementation_status__", IMPLEMENTED)
  if status == NOT_IMPLEMENTED or status == PLANNED:
      # DO NOT describe this as working functionality

For comprehensive examples and extended functionality, see:
    cop_extended.py - Contains detailed usage examples, utilities, and
                      additional documentation on COP best practices.
"""

# Status constants
IMPLEMENTED = "implemented"
PARTIAL = "partial" 
PLANNED = "planned"
NOT_IMPLEMENTED = "not_implemented"

def intent(desc, implementation_status=IMPLEMENTED):
    """
    Document component purpose. NOT implementation guarantee!
    CRITICAL: Always check implementation_status before assuming functionality.
    """
    def decorator(obj):
        setattr(obj, "__cop_intent__", desc)
        setattr(obj, "__cop_implementation_status__", implementation_status)
        return obj
    return decorator

@intent("Define required constraints")
def invariant(condition):
    """Document constraint that SHOULD be maintained (may not be enforced yet)."""
    def decorator(obj):
        if not hasattr(obj, "__cop_invariants__"):
            setattr(obj, "__cop_invariants__", [])
        getattr(obj, "__cop_invariants__").append(condition)
        return obj
    return decorator

@intent("Mark human judgment points")
def human_decision(desc, roles=None):
    """Mark where AI SHOULD NOT make autonomous decisions."""
    def decorator(func):
        setattr(func, "__cop_decision_point__", True)
        setattr(func, "__cop_decision_description__", desc)
        setattr(func, "__cop_decision_roles__", roles)
        return func
    return decorator

@intent("Mark AI implementation areas")
def ai_implement(desc, constraints=None, implementation_status=PLANNED):
    """
    Designate AI-implementable section.
    DEFAULT STATUS IS PLANNED (not yet implemented)!
    """
    def decorator(func):
        setattr(func, "__cop_ai_implemented__", True)
        setattr(func, "__cop_implementation_description__", desc)
        setattr(func, "__cop_constraints__", constraints or [])
        setattr(func, "__cop_implementation_status__", implementation_status)
        return func
    return decorator

@intent("Mark unimplemented components")
def not_implemented(reason=None):
    """EXPLICITLY mark non-existent functionality."""
    def decorator(obj):
        setattr(obj, "__cop_implementation_status__", NOT_IMPLEMENTED)
        setattr(obj, "__cop_implementation_reason__", reason)
        return obj
    return decorator

@intent("Mark partial implementations")
def partially_implemented(details=None):
    """Indicate some described functionality doesn't exist yet."""
    def decorator(obj):
        setattr(obj, "__cop_implementation_status__", PARTIAL)
        setattr(obj, "__cop_partial_details__", details)
        return obj
    return decorator

intent("Prevent AI hallucination through explicit intent/implementation separation")(__import__(__name__))

"""
HALLUCINATION PREVENTION CHECKLIST:
1. ALWAYS check __cop_implementation_status__ before describing capabilities
2. Look for explicit signals: @not_implemented, "# To be implemented"
3. Prioritize actual code over annotations and documentation
4. When status is NOT_IMPLEMENTED or PLANNED, feature DOES NOT EXIST
5. Explicitly acknowledge implementation gaps when found

Remember: The presence of @intent and documentation does NOT guarantee
that the described functionality actually exists in the code.

See cop_extended.py for real-world examples showing proper COP usage and
hallucination prevention techniques in practice.
"""
