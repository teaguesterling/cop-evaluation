"""
Test relationship decorators for the financial processor example.

These decorators are used to link test functions to specific components
and COP annotations for comprehensive verification tracking.
"""

def test_for(component, **kwargs):
    """
    Decorator to indicate that a test verifies a specific component.
    
    Args:
        component: The component being tested (e.g., "PaymentProcessor.process_payment")
        **kwargs: Additional parameters like test_type ("unit", "integration", etc.)
    """
    def decorator(func):
        func._test_for_component = component
        func._test_type = kwargs.get('test_type', 'unit')
        return func
    return decorator


def test_invariant(component, invariant_value):
    """
    Decorator to indicate that a test verifies a specific invariant.
    
    Args:
        component: The component whose invariant is being tested
        invariant_value: The invariant condition being verified
    """
    def decorator(func):
        func._test_for_component = component
        func._test_annotation_type = 'invariant'
        func._test_annotation_value = invariant_value
        func._test_type = 'unit'
        return func
    return decorator


def test_risk(component, risk_value):
    """
    Decorator to indicate that a test verifies risk scenarios.
    
    Args:
        component: The component whose risk is being tested
        risk_value: The risk level being tested ("LOW", "MEDIUM", "HIGH", "CRITICAL")
    """
    def decorator(func):
        func._test_for_component = component
        func._test_annotation_type = 'risk'
        func._test_annotation_value = risk_value
        func._test_type = 'unit'
        return func
    return decorator


def test_implementation_status(component, status_value):
    """
    Decorator to indicate that a test verifies implementation status.
    
    Args:
        component: The component whose implementation status is being tested
        status_value: The status being tested ("IMPLEMENTED", "PARTIAL", "NOT_IMPLEMENTED")
    """
    def decorator(func):
        func._test_for_component = component
        func._test_annotation_type = 'implementation_status'
        func._test_annotation_value = status_value
        func._test_type = 'unit'
        return func
    return decorator


def test_decision(component, decision_value):
    """
    Decorator to indicate that a test verifies decision boundaries.
    
    Args:
        component: The component whose decision is being tested
        decision_value: The decision type being tested ("HUMAN", "AI")
    """
    def decorator(func):
        func._test_for_component = component
        func._test_annotation_type = 'decision'
        func._test_annotation_value = decision_value
        func._test_type = 'unit'
        return func
    return decorator


def integration_test(component):
    """
    Decorator for integration tests.
    
    Args:
        component: The component being tested in integration
    """
    def decorator(func):
        func._test_for_component = component
        func._test_type = 'integration'
        return func
    return decorator


def security_test(component):
    """
    Decorator for security-focused tests.
    
    Args:
        component: The component being tested for security
    """
    def decorator(func):
        func._test_for_component = component
        func._test_type = 'security'
        return func
    return decorator