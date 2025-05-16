"""
ASSERTIONS MODULE FOR COP TESTING

This module provides specialized assertion functions for testing
code that uses COP annotations, particularly for verifying
critical invariants, security requirements, and implementation status.
"""

import inspect
from typing import Any, Callable, Optional, Type, Dict

from .core import COPAnnotation, get_current_annotations, security_risk, critical_invariant, implementation_status
from .testing import TestingException

class InvariantViolation(TestingException):
    """Raised when a critical invariant is violated."""
    pass

class SecurityRiskViolation(TestingException):
    """Raised when a security requirement is violated."""
    pass

class ImplementationStatusMismatch(TestingException):
    """Raised when implementation status doesn't match reality."""
    pass

def assert_invariant(condition: bool, message: Optional[str] = None):
    """
    Assert that a critical invariant is maintained.
    
    Args:
        condition: The condition that must be true for the invariant to hold
        message: Optional custom error message
        
    Raises:
        InvariantViolation: If the condition is false
    """
    if not condition:
        # Extract the current critical invariant context if available
        invariants = get_current_annotations(critical_invariant)
        inv_context = f" (violates: {invariants[-1].condition})" if invariants else ""
        
        msg = message or f"Invariant violation{inv_context}"
        raise InvariantViolation(msg)

def assert_security_requirement(condition: bool, message: Optional[str] = None):
    """
    Assert that a security requirement is met.
    
    Args:
        condition: The condition that must be true for the requirement to be met
        message: Optional custom error message
        
    Raises:
        SecurityRiskViolation: If the condition is false
    """
    if not condition:
        # Extract the current security risk context if available
        risks = get_current_annotations(security_risk)
        risk_context = f" (exposes risk: {risks[-1].description})" if risks else ""
        
        msg = message or f"Security requirement violation{risk_context}"
        raise SecurityRiskViolation(msg)

def assert_implementation_matches_status(component: Any, behavior_works: bool, message: Optional[str] = None):
    """
    Assert that component behavior matches its implementation status.
    
    Args:
        component: The component with implementation status
        behavior_works: Whether the behavior was successful
        message: Optional custom error message
        
    Raises:
        ImplementationStatusMismatch: If behavior doesn't match status
    """
    status = getattr(component, "__cop_implementation_status__", "implemented")
    
    if status in ["implemented", "partial"] and not behavior_works:
        details = getattr(component, "__cop_implementation_details__", "")
        details_str = f" ({details})" if details else ""
        raise ImplementationStatusMismatch(
            message or f"Component marked as {status}{details_str} but behavior failed"
        )
    
    if status in ["not_implemented", "planned"] and behavior_works:
        raise ImplementationStatusMismatch(
            message or f"Component marked as {status} but behavior works"
        )

def assert_context_has(annotation_type: Type[COPAnnotation], 
                      context: Dict, 
                      property_name: str, 
                      expected_value: Any):
    """
    Assert that an annotation context has a specific property value.
    
    Args:
        annotation_type: The type of annotation to check
        context: The context dict containing annotations
        property_name: The name of the property to check
        expected_value: The expected value of the property
        
    Raises:
        AssertionError: If the property doesn't exist or has wrong value
    """
    annotations = context.get(annotation_type.__name__, [])
    
    if not annotations:
        raise AssertionError(f"No {annotation_type.__name__} annotations in context")
    
    for annotation in annotations:
        if hasattr(annotation, property_name):
            property_value = getattr(annotation, property_name)
            if property_value == expected_value:
                return
    
    raise AssertionError(
        f"No {annotation_type.__name__} annotation with {property_name}={expected_value} in context"
    )

def assert_security_tested(component: Any, message: Optional[str] = None):
    """
    Assert that a component with security risks has security tests.
    
    Args:
        component: The component to check
        message: Optional custom error message
        
    Raises:
        AssertionError: If component has security risks but no security tests
    """
    # Check if component has security risks
    has_security_risk = hasattr(component, "__cop_security_risk__")
    
    if not has_security_risk:
        return  # No security risks, no need for security tests
    
    # Check if there are security tests for this component
    has_security_tests = False
    
    # This is a simplified check - in a real implementation, would look for actual tests
    component_module = inspect.getmodule(component)
    component_name = component.__name__ if hasattr(component, "__name__") else str(component)
    
    try:
        import importlib
        test_module_name = f"tests.test_{component_module.__name__}"
        test_module = importlib.import_module(test_module_name)
        
        test_functions = [
            name for name, obj in inspect.getmembers(test_module, inspect.isfunction)
            if name.startswith(f"test_{component_name}") and "security" in name
        ]
        
        has_security_tests = len(test_functions) > 0
    except (ImportError, AttributeError):
        # Could not find test module or component has no module
        has_security_tests = False
    
    if not has_security_tests:
        raise AssertionError(message or 
                            f"Component has security risks but no security tests: {component_name}")

def assert_critical_invariants_tested(component: Any, message: Optional[str] = None):
    """
    Assert that a component with critical invariants has tests for those invariants.
    
    Args:
        component: The component to check
        message: Optional custom error message
        
    Raises:
        AssertionError: If component has critical invariants but no tests for them
    """
    # Check if component has critical invariants
    has_critical_invariants = hasattr(component, "__cop_critical_invariants__")
    
    if not has_critical_invariants:
        return  # No critical invariants, no need for specific tests
    
    # Get the invariants
    invariants = getattr(component, "__cop_critical_invariants__", [])
    
    if not invariants:
        return  # Empty list, no need for tests
    
    # Check if there are tests for this component
    component_module = inspect.getmodule(component)
    component_name = component.__name__ if hasattr(component, "__name__") else str(component)
    
    has_invariant_tests = False
    
    try:
        import importlib
        test_module_name = f"tests.test_{component_module.__name__}"
        test_module = importlib.import_module(test_module_name)
        
        # Look for test functions that might test invariants
        test_functions = [
            name for name, obj in inspect.getmembers(test_module, inspect.isfunction)
            if name.startswith(f"test_{component_name}") and (
                "invariant" in name or 
                "constraint" in name or 
                "property" in name
            )
        ]
        
        has_invariant_tests = len(test_functions) > 0
    except (ImportError, AttributeError):
        # Could not find test module or component has no module
        has_invariant_tests = False
    
    if not has_invariant_tests:
        raise AssertionError(message or 
                            f"Component has critical invariants but no invariant tests: {component_name}")
