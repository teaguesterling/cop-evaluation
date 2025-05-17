"""
Assertion functions for verifying COP annotations through tests.

These are standalone versions of the assertion methods available 
through the enhanced annotation classes.
"""

from typing import Any, Optional, Dict, Type, Callable

# Re-export the exception classes
from .annotations import (
    InvariantViolation,
    SecurityRiskViolation,
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


def assert_maintained(condition: bool, invariant_description: str, *, on: Any = None) -> None:
    """
    Assert that an invariant is maintained after operations.
    
    This is a standalone version of invariant.assert_maintained().
    
    Args:
        condition: Whether the invariant holds true
        invariant_description: Description of the invariant
        on: Optional component to validate against
    """
    from .annotations import invariant
    invariant.assert_maintained(condition, invariant_description, on=on)


def assert_violation_raises(expected_exception: Type[Exception], 
                           callable_obj: Callable, 
                           *args, 
                           invariant_description: Optional[str] = None, 
                           **kwargs) -> None:
    """
    Assert that violating an invariant raises the expected exception.
    
    This is a standalone version of invariant.assert_violation_raises().
    
    Args:
        expected_exception: Exception that should be raised
        callable_obj: Callable that should raise the exception
        *args, **kwargs: Arguments to pass to the callable
        invariant_description: Description of the invariant being tested
        
    Raises:
        AssertionError: If the callable doesn't raise the expected exception
    """
    from .annotations import invariant
    invariant.assert_violation_raises(expected_exception, callable_obj, 
                                     *args, 
                                     invariant_description=invariant_description, 
                                     **kwargs)


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


def assert_mitigated(condition: bool, risk_description: str, *, on: Any = None) -> None:
    """
    Assert that a security risk has been mitigated.
    
    This is a standalone version of risk.assert_mitigated().
    
    Args:
        condition: Whether the mitigation is in place
        risk_description: Description of the risk
        on: Optional component to validate against
    """
    from .annotations import risk
    risk.assert_mitigated(condition, risk_description, on=on)


def assert_prevented(attack_function: Callable, 
                    *args, 
                    risk_description: Optional[str] = None, 
                    **kwargs) -> None:
    """
    Assert that a security attack is prevented.
    
    This is a standalone version of risk.assert_prevented().
    
    Args:
        attack_function: Function that attempts an attack
        *args, **kwargs: Arguments to pass to the attack function
        risk_description: Description of the risk being tested
        
    Raises:
        AssertionError: If the attack function succeeds
    """
    from .annotations import risk
    risk.assert_prevented(attack_function, *args, risk_description=risk_description, **kwargs)


def assert_sanitized(value: Any, 
                    sanitizer: Callable, 
                    risk_description: Optional[str] = None, 
                    *, 
                    on: Any = None) -> None:
    """
    Assert that input is properly sanitized.
    
    This is a standalone version of risk.assert_sanitized().
    
    Args:
        value: The potentially dangerous value
        sanitizer: Function that should sanitize the value
        risk_description: Description of the risk
        on: Optional component to validate against
    """
    from .annotations import risk
    risk.assert_sanitized(value, sanitizer, risk_description, on=on)


#---------------------- Implementation Status Assertions ----------------------#

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


def assert_completeness(component: Any, features: Dict[str, bool]) -> None:
    """
    Assert implementation completeness against a set of features.
    
    This is a standalone version of implementation_status.assert_completeness().
    
    Args:
        component: The component to check
        features: Dict mapping feature names to whether they should work
        
    Example:
        assert_completeness(my_component, {
            "basic_functionality": True,   # Should work
            "advanced_features": False,    # Should not work yet
        })
    """
    from .annotations import implementation_status
    implementation_status.assert_completeness(component, features)


#---------------------- Decision Assertions ----------------------#

def assert_decision_followed(condition: bool, question: str, *, on: Any = None) -> None:
    """
    Assert that a decision has been followed correctly.
    
    This is a standalone version of decision.assert_followed().
    
    Args:
        condition: Whether the decision was followed correctly
        question: The decision question
        on: Optional component to validate against
    """
    from .annotations import decision
    decision.assert_followed(condition, question, on=on)


def assert_constraints_met(constraints: Dict[str, bool], *, on: Any = None) -> None:
    """
    Assert that decision constraints have been met.
    
    This is a standalone version of decision.assert_constraints_met().
    
    Args:
        constraints: Dict mapping constraint descriptions to whether they're met
        on: Optional component to validate against
        
    Example:
        assert_constraints_met({
            "Use Stripe for processing": uses_stripe(payment),
            "Support refunds": supports_refunds(payment),
        }, on=process_payment)
    """
    from .annotations import decision
    decision.assert_constraints_met(constraints, on=on)


#---------------------- Intent Assertions ----------------------#

def assert_intent_fulfilled(condition: bool, intent_description: str, *, on: Any = None) -> None:
    """
    Assert that an intent is fulfilled by the implementation.
    
    This is a standalone version of intent.assert_fulfilled().
    
    Args:
        condition: Whether the intent is fulfilled
        intent_description: Description of the intent
        on: Optional component to validate against
    """
    from .annotations import intent
    intent.assert_fulfilled(condition, intent_description, on=on)


def assert_achieves_goal(goal_achieved: bool, intent_description: str, *, on: Any = None) -> None:
    """
    Assert that the code achieves its intended goal.
    
    This is a standalone version of intent.assert_achieves_goal().
    
    Args:
        goal_achieved: Whether the intended goal was achieved
        intent_description: Description of the intent
        on: Optional component to validate against
    """
    from .annotations import intent
    intent.assert_achieves_goal(goal_achieved, intent_description, on=on)
