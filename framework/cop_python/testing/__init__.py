"""
🚨 CONCEPT-ORIENTED PROGRAMMING: TESTING FRAMEWORK 🚨

=====================================================================
| This module connects tests to COP annotations, completing the     |
| decision tetrahedron by enabling verification of implementation   |
| against intent and decisions.                                     |
=====================================================================

🎯 INTENT: What code is supposed to do (from annotations)
🛠️ IMPLEMENTATION: What code actually does (from implementation)
✅ TESTS: Verification that implementation fulfills intent
🤔 DECISIONS: Why specific approaches were chosen

CORE USAGE PATTERNS:
---------------------------------------------------------------------

1️⃣ LINK TESTS TO COMPONENTS:
   @invariant.test_for(process_payment, "Transactions must be atomic")
   def test_transaction_atomicity():
       # Test that verifies this invariant on this component

2️⃣ DEFINE EXTERNALIZED INVARIANTS:
   invariant.on(process_payment, "Currency must be supported")
   # Defines invariant in tests without cluttering implementation

3️⃣ VERIFY IMPLEMENTATION STATUS:
   @implementation_status.test_for(process_payment, IMPLEMENTED)
   def test_implementation_completeness():
       # Verifies process_payment is fully implemented

4️⃣ VERIFY SECURITY RISKS:
   @risk.test_for(process_payment, "Card data exposure", severity="HIGH")
   def test_card_data_security():
       # Verifies risk mitigation on this component

5️⃣ VERIFY DECISION IMPLEMENTATION:
   @decision.test_for(process_payment, "Use Stripe for payment processing")
   def test_decision_implementation():
       # Verifies decision was implemented correctly

SPECIALIZED ASSERTIONS:
---------------------------------------------------------------------
assert_invariant(condition, message=None, on=None)
assert_maintained(condition, invariant_description, on=None)
assert_violation_raises(expected_exception, callable_obj, *args, **kwargs)

assert_security_requirement(condition, message=None, on=None)
assert_mitigated(condition, risk_description, on=None)
assert_prevented(attack_function, *args, **kwargs)
assert_sanitized(value, sanitizer, risk_description=None, on=None)

assert_implementation_matches_status(component, behavior_success)
assert_completeness(component, features)

assert_decision_followed(condition, question, on=None)
assert_constraints_met(constraints, on=None)

assert_intent_fulfilled(condition, intent_description, on=None)
assert_achieves_goal(goal_achieved, intent_description, on=None)

⚠️ PREVENT META-DISTRACTION:
1. Focus on what the tests verify, not the testing framework itself
2. Keep annotations minimal - less is more
3. Prioritize clear, direct connections between tests and components
4. Security risks should have explicit test verification
"""

# Re-export testing-enhanced annotations
from .annotations import (
    intent, 
    invariant, 
    implementation_status, 
    risk, 
    decision
)

# Re-export exception classes
from .annotations import (
    InvariantViolation,
    SecurityRiskViolation,
    ImplementationStatusMismatch,
    DecisionViolation,
    IntentViolation
)

# Re-export all assertion functions
from .assertions import (
    # Invariant assertions
    assert_invariant,
    assert_maintained,
    assert_violation_raises,
    
    # Security risk assertions
    assert_security_requirement,
    assert_mitigated,
    assert_prevented,
    assert_sanitized,
    
    # Implementation status assertions
    assert_implementation_matches_status,
    assert_completeness,
    
    # Decision assertions
    assert_decision_followed,
    assert_constraints_met,
    
    # Intent assertions
    assert_intent_fulfilled,
    assert_achieves_goal
)

# Re-export verification tools
from .verification import (
    check_component_test_coverage,
    generate_verification_report
)

# Re-export implementation status constants
from ..core import (
    # Implementation states
    IMPLEMENTED,         # ✅ Fully functional and complete
    PARTIAL,             # ⚠️ Partially working with limitations
    PLANNED,             # 📝 Designed but not implemented
    NOT_IMPLEMENTED,     # ❓ Does not exist at all
    BUGGY,               # ❌ Was working but now has issues
    DEPRECATED           # 🚫 Exists but should not be used
)

# Export pytest plugin for auto-discovery
from .integration import pytest_plugin

# Define what is exported
__all__ = [
    # Enhanced annotations
    'intent', 'invariant', 'implementation_status', 'risk', 'decision',
    
    # Exception classes
    'InvariantViolation', 'SecurityRiskViolation', 'ImplementationStatusMismatch',
    'DecisionViolation', 'IntentViolation',
    
    # Invariant assertions
    'assert_invariant', 'assert_maintained', 'assert_violation_raises',
    
    # Security risk assertions
    'assert_security_requirement', 'assert_mitigated', 'assert_prevented', 'assert_sanitized',
    
    # Implementation status assertions
    'assert_implementation_matches_status', 'assert_completeness',
    
    # Decision assertions
    'assert_decision_followed', 'assert_constraints_met',
    
    # Intent assertions
    'assert_intent_fulfilled', 'assert_achieves_goal',
    
    # Verification tools
    'check_component_test_coverage', 'generate_verification_report',
    
    # Implementation status constants
    'IMPLEMENTED', 'PARTIAL', 'PLANNED', 'NOT_IMPLEMENTED', 'BUGGY', 'DEPRECATED',
    
    # Pytest plugin
    'pytest_plugin'
]
