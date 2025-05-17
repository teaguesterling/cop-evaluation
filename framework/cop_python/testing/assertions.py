"""
Assertion functions for verifying COP annotations through tests.

These are standalone versions of the assertion methods available 
through the enhanced annotation classes.
"""

# Re-export the exception classes
from .annotations import (
    InvariantViolation,
    SecurityRiskViolation,
    ImplementationStatusMismatch,
    DecisionViolation,
    IntentViolation
)

def assert_invariant(condition: bool, message: Optional[str] = None, *, on: Any = None) -> None:
    """
    Assert that an invariant is maintained.
    
    This is a standalone version of invariant.assertion().
    
    Args:
        condition: The condition that must be true
        message: Optional message or specific invariant to check
        on: Optional component to validate against
    """
    from .annotations import invariant
    invariant.assertion(condition, message, on=on)


def assert_security_requirement(condition: bool, message: Optional[str] = None, *, on: Any = None) -> None:
    """
    Assert that a security requirement is met.
    
    This is a standalone version of risk.assertion().
    
    Args:
        condition: The condition that must be true
        message: Optional message or specific risk to check
        on: Optional component to validate against
    """
    from .annotations import risk
    risk.assertion(condition, message, on=on)


def assert_implementation_matches_status(component: Any, behavior_success: bool) -> None:
    """
    Assert that implementation status matches actual behavior.
    
    This is a standalone version of implementation_status.assert_matches().
    
    Args:
        component: The component to check
        behavior_success: Whether the behavior was successful
    """
    from .annotations import implementation_status
    implementation_status.assert_matches(component, behavior_success)
