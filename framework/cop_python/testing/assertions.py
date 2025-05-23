"""
Assertion functions for verifying COP annotations through tests.

These are standalone versions of the assertion methods available 
through the enhanced annotation classes.
"""

from typing import Any, Optional, Dict, Type, Callable

# Re-export the exception classes
from .foundation import (
    InvariantViolation,
    RiskViolation,
    ImplementationStatusMismatch,
    DecisionViolation,
    IntentViolation
)

#---------------------- Invariant Assertions ----------------------#

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


#---------------------- Security Risk Assertions ----------------------#

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


#---------------------- Implementation Status Assertions ----------------------#

def assert_implemented(condition: bool, message: Optional[str] = None, *, on: Any = None) -> None:
    """
    Assert that a feature is properly implemented.
    
    This is a standalone version of implementation_status.assertion().
    
    Args:
        condition: The condition that must be true
        message: Optional message about implementation status
        on: Optional component to validate against
    """
    from .annotations import implementation_status
    implementation_status.assertion(condition, message, on=on)


#---------------------- Decision Assertions ----------------------#

def assert_decision(condition: bool, message: Optional[str] = None, *, on: Any = None) -> None:
    """
    Assert that a design decision is followed.
    
    This is a standalone version of decision.assertion().
    
    Args:
        condition: The condition that must be true
        message: Optional message about the decision
        on: Optional component to validate against
    """
    from .annotations import decision
    decision.assertion(condition, message, on=on)


#---------------------- Intent Assertions ----------------------#

def assert_intent(condition: bool, message: Optional[str] = None, *, on: Any = None) -> None:
    """
    Assert that an intent is fulfilled.
    
    This is a standalone version of intent.assertion().
    
    Args:
        condition: The condition that must be true
        message: Optional message about the intent
        on: Optional component to validate against
    """
    from .annotations import intent
    intent.assertion(condition, message, on=on)