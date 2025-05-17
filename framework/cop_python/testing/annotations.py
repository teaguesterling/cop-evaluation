# cop_python/testing/annotations.py
import functools
from typing import Any, Optional, Type, Dict
from ..core import (
    COPAnnotation, 
    intent as core_intent,
    implementation_status as core_implementation_status,
    risk as core_risk,
    invariant as core_invariant,
    decision as core_decision
)

# Define exception classes here so we don't need a separate exceptions.py
class COPAnnotationViolation(AssertionError):
    """Base class for all COP annotation violations."""
    pass

class InvariantViolation(COPAnnotationViolation):
    """Raised when an invariant is violated."""
    pass

class SecurityRiskViolation(COPAnnotationViolation):
    """Raised when a security requirement is violated."""
    pass

class ImplementationStatusMismatch(COPAnnotationViolation):
    """Raised when implementation status doesn't match reality."""
    pass

class DecisionViolation(COPAnnotationViolation):
    """Raised when a decision implementation is violated."""
    pass

class IntentViolation(COPAnnotationViolation):
    """Raised when code doesn't fulfill its intent."""
    pass


class COPAnnotationTestingMixin:
    """Mixin that adds testing capabilities to COP annotations."""
    
    @classmethod
    def test_for(cls, component, *args, **kwargs):
        """
        Create a test decorator that verifies this type of annotation on a specific component.
        
        Args:
            component: The component whose annotation is being tested
            *args, **kwargs: Arguments matching the annotation being tested
            
        Returns:
            A decorator function for test methods
        """
        def decorator(test_func):
            # Store annotation parameters on the test function
            attr_name = f"__cop_verifies_{cls.__name__}__"
            verification_info = {
                "args": args,
                "kwargs": kwargs,
                "annotation_type": cls.__name__,
                "component": component,
                "component_name": getattr(component, "__name__", str(component))
            }
            setattr(test_func, attr_name, verification_info)
            
            @functools.wraps(test_func)
            def wrapper(*test_args, **test_kwargs):
                # Run the test
                result = test_func(*test_args, **test_kwargs)
                
                # Record test execution for verification tracking
                _record_test_verification(test_func, verification_info)
                
                return result
            
            return wrapper
        
        return decorator
    
    @classmethod
    def on(cls, component, *args, **kwargs):
        """
        Apply an annotation to a component from test code.
        
        This method allows applying annotations to components from
        test files without modifying the implementation code.
        
        Args:
            component: The component to annotate
            *args, **kwargs: Arguments for the annotation
            
        Returns:
            The component with the applied annotation
        """
        # Create the annotation
        annotation = cls(*args, **kwargs)
        
        # Apply it to the component
        component = annotation._apply_to_object(component)
        
        # Mark this as an externalized annotation
        attr_name = f"__cop_{cls.__name__}s__"
        if hasattr(component, attr_name):
            annotations = getattr(component, attr_name)
            if isinstance(annotations, list):
                # Find the last added annotation (the one we just added)
                if annotations:
                    annotations[-1]["externalized"] = True
            elif annotations:
                # Convert to dict if not already
                if not isinstance(annotations, dict):
                    annotations = {"value": annotations}
                annotations["externalized"] = True
                setattr(component, attr_name, annotations)
        
        return component
    
    @classmethod
    def verify(cls, *args, **kwargs):
        """
        Create a context manager for verifying an annotation during a test.
        
        This method returns a context manager that can be used in a 'with'
        statement to verify that a specific annotation is maintained during
        the enclosed code block.
        
        Returns:
            A context manager for verification
        """
        # Create the annotation
        annotation = cls(*args, **kwargs)
        
        # The context manager will track when this annotation is active
        class VerificationContext:
            def __enter__(self):
                annotation._enter_context()
                return self
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                # Check if the verification was successful
                if exc_type is not None:
                    # An exception occurred - check if it's a test assertion
                    if issubclass(exc_type, AssertionError):
                        # Record the verification failure
                        _record_verification_failure(cls.__name__, args, kwargs, exc_val)
                
                annotation._exit_context()
                return False  # Don't suppress exceptions
        
        return VerificationContext()
    
    @classmethod
    def _get_exception_class(cls) -> Type[AssertionError]:
        """Get the appropriate exception class for this annotation type."""
        return cls.__cop_assertion_exception__
    
    @classmethod
    def _validate_annotation_exists(cls, message: str, on: Any) -> bool:
        """Validate that the specified annotation exists on the component."""
        if not message or not on:
            return True
            
        annotation_type = cls.__name__
        
        # Get the appropriate attribute name for this annotation type
        attr_name = f"__cop_{annotation_type}s__"
        if annotation_type == "implementation_status":
            attr_name = f"__cop_{annotation_type}__"
        
        # Check if this specific annotation exists on the component
        if not hasattr(on, attr_name):
            return False
            
        annotations = getattr(on, attr_name)
        
        if annotation_type == "implementation_status":
            # Special case for implementation_status
            return annotations == message
        elif isinstance(annotations, list):
            # List of annotations (invariants, risks, etc.)
            return any(
                (isinstance(a, dict) and (
                    a.get("condition") == message or 
                    a.get("description") == message or
                    a.get("question") == message
                )) or 
                (isinstance(a, str) and a == message)
                for a in annotations
            )
        
        return False
    
    @classmethod
    def _build_error_message(cls, message: Optional[str], on: Optional[Any]) -> str:
        """Build an appropriate error message with component info if available."""
        annotation_type = cls.__name__
        
        component_info = ""
        if on:
            component_name = getattr(on, "__name__", str(on))
            component_info = f" on {component_name}"
        
        return message or f"{annotation_type.title()} violation{component_info}"
    
    @classmethod
    def assert_condition(cls, condition: bool, message: Optional[str] = None, *, on: Any = None) -> None:
        """
        Assert that a condition related to this annotation type is true.
        
        This method creates type-specific assertions that validate conditions
        related to the annotation type (invariant, risk, etc.).
        
        Args:
            condition: The condition that must be true
            message: Optional message or specific annotation value to check
            on: Optional component to validate against
            
        Raises:
            AssertionError: If the condition is false
        """
        if not condition:
            # Optionally validate the annotation exists
            if on and message:
                exists = cls._validate_annotation_exists(message, on)
                if not exists:
                    # Could log a warning here
                    pass
            
            # Build the error message
            error_message = cls._build_error_message(message, on)
            
            # Get the appropriate exception class
            exception_class = cls._get_exception_class()
            
            # Raise the exception
            raise exception_class(error_message)
    
    # Alias for better readability
    @classmethod
    def assertion(cls, condition: bool, message: Optional[str] = None, *, on: Any = None) -> None:
        """Alias for assert_condition with more natural syntax."""
        cls.assert_condition(condition, message, on=on)


class COPAnnotationInvariantTestingMixin(COPAnnotationTestingMixin):
    __cop_assertion_exception__ = InvariantViolation
    
    @classmethod
    def assert_maintained(cls, condition: bool, invariant_description: str, *, on: Any = None) -> None:
        """
        Assert that an invariant is maintained after operations.
        
        Args:
            condition: Whether the invariant holds true
            invariant_description: Description of the invariant
            on: Optional component to validate against
        """
        cls.assert_condition(condition, invariant_description, on=on)
    
    @classmethod
    def assert_violation_raises(cls, expected_exception, callable_obj, *args, invariant_description: str = None, **kwargs):
        """
        Assert that violating an invariant raises the expected exception.
        
        Args:
            expected_exception: Exception that should be raised
            callable_obj: Callable that should raise the exception
            *args, **kwargs: Arguments to pass to the callable
            invariant_description: Description of the invariant being tested
            
        Raises:
            AssertionError: If the callable doesn't raise the expected exception
        """
        try:
            callable_obj(*args, **kwargs)
        except expected_exception:
            return  # Test passed
        except Exception as e:
            raise AssertionError(f"Expected {expected_exception.__name__}, but got {type(e).__name__}: {str(e)}")
        
        raise AssertionError(f"Expected {expected_exception.__name__} for violating '{invariant_description}', but no exception was raised")


class COPAnnotationRiskTestingMixin(COPAnnotationTestingMixin):
    __cop_assertion_exception__ = SecurityRiskViolation
    
    @classmethod
    def assert_mitigated(cls, condition: bool, risk_description: str, *, on: Any = None) -> None:
        """
        Assert that a security risk has been mitigated.
        
        Args:
            condition: Whether the mitigation is in place
            risk_description: Description of the risk
            on: Optional component to validate against
        """
        cls.assert_condition(condition, risk_description, on=on)

    @classmethod
    def assert_prevented(cls, attack_function, *args, risk_description: str = None, **kwargs):
        """
        Assert that a security attack is prevented.
        
        Args:
            attack_function: Function that attempts an attack
            *args, **kwargs: Arguments to pass to the attack function
            risk_description: Description of the risk being tested
            
        Raises:
            AssertionError: If the attack function succeeds
        """
        try:
            result = attack_function(*args, **kwargs)
            raise AssertionError(f"Attack function succeeded when it should have been prevented: {result}")
        except Exception:
            # Attack was prevented by raising an exception
            pass
    
    @classmethod
    def assert_sanitized(cls, value, sanitizer, risk_description: str = None, *, on: Any = None):
        """
        Assert that input is properly sanitized.
        
        Args:
            value: The potentially dangerous value
            sanitizer: Function that should sanitize the value
            risk_description: Description of the risk
            on: Optional component to validate against
        """
        original = str(value)
        sanitized = sanitizer(value)
        
        if original == sanitized and any(char in original for char in '<>&"\'/'):
            raise SecurityRiskViolation(f"Input not sanitized: {original}")


class COPAnnotationDecisionTestingMixin(COPAnnotationTestingMixin):
    __cop_assertion_exception__ = DecisionViolation
    
    @classmethod
    def assert_followed(cls, condition: bool, question: str, *, on: Any = None) -> None:
        """
        Assert that a decision has been followed correctly.
        
        Args:
            condition: Whether the decision was followed correctly
            question: The decision question
            on: Optional component to validate against
        """
        cls.assert_condition(condition, question, on=on)
    
    @classmethod
    def assert_constraints_met(cls, constraints: Dict[str, bool], *, on: Any = None) -> None:
        """
        Assert that decision constraints have been met.
        
        Args:
            constraints: Dict mapping constraint descriptions to whether they're met
            on: Optional component to validate against
            
        Example:
            decision.assert_constraints_met({
                "Use Stripe for processing": uses_stripe(payment),
                "Support refunds": supports_refunds(payment),
            }, on=process_payment)
        """
        mismatches = []
        for constraint, is_met in constraints.items():
            if not is_met:
                mismatches.append(constraint)
        
        if mismatches:
            component_info = ""
            if on:
                component_name = getattr(on, "__name__", str(on))
                component_info = f" in {component_name}"
                
            raise DecisionViolation(
                f"Decision constraints not met{component_info}:\n" +
                "\n".join(f"- {constraint}" for constraint in mismatches)
            )


class COPAnnotationIntentTestingMixin(COPAnnotationTestingMixin):
    __cop_assertion_exception__ = IntentViolation
    
    @classmethod
    def assert_fulfilled(cls, condition: bool, intent_description: str, *, on: Any = None) -> None:
        """
        Assert that an intent is fulfilled by the implementation.
        
        Args:
            condition: Whether the intent is fulfilled
            intent_description: Description of the intent
            on: Optional component to validate against
        """
        cls.assert_condition(condition, intent_description, on=on)
    
    @classmethod
    def assert_achieves_goal(cls, goal_achieved: bool, intent_description: str, *, on: Any = None) -> None:
        """
        Assert that the code achieves its intended goal.
        
        Args:
            goal_achieved: Whether the intended goal was achieved
            intent_description: Description of the intent
            on: Optional component to validate against
        """
        cls.assert_condition(goal_achieved, intent_description, on=on)


class COPAnnotationImplementationStatusTestingMixin(COPAnnotationTestingMixin):
    __cop_assertion_exception__ = ImplementationStatusMismatch
    
    @classmethod
    def assert_matches(cls, component: Any, behavior_success: bool) -> None:
        """
        Assert that implementation status matches actual behavior.
        
        Args:
            component: The component to check
            behavior_success: Whether the behavior was successful
        """
        status = getattr(component, "__cop_implementation_status__", "implemented")
        
        if status in ["implemented", "partial"] and not behavior_success:
            details = getattr(component, "__cop_implementation_details__", "")
            details_str = f" ({details})" if details else ""
            
            component_name = getattr(component, "__name__", str(component))
            raise ImplementationStatusMismatch(
                f"{component_name} is marked as {status}{details_str} but behavior failed"
            )
        
        if status in ["not_implemented", "planned"] and behavior_success:
            component_name = getattr(component, "__name__", str(component))
            raise ImplementationStatusMismatch(
                f"{component_name} is marked as {status} but behavior works"
            )
    
    @classmethod
    def assert_completeness(cls, component: Any, features: Dict[str, bool]) -> None:
        """
        Assert implementation completeness against a set of features.
        
        Args:
            component: The component to check
            features: Dict mapping feature names to whether they should work
            
        Example:
            implementation_status.assert_completeness(my_component, {
                "basic_functionality": True,   # Should work
                "advanced_features": False,    # Should not work yet
            })
        """
        status = getattr(component, "__cop_implementation_status__", "implemented")
        component_name = getattr(component, "__name__", str(component))
        
        mismatches = []
        for feature, should_work in features.items():
            try:
                # Try to use the feature
                feature_fn = getattr(component, feature, None)
                if feature_fn is None:
                    if should_work:
                        mismatches.append(f"Feature '{feature}' not found but should work")
                    continue
                
                result = feature_fn()
                works = bool(result)
                
                if works != should_work:
                    mismatches.append(
                        f"Feature '{feature}' {'works but shouldn't' if works else 'doesn't work but should'}"
                    )
            except Exception as e:
                if should_work:
                    mismatches.append(f"Feature '{feature}' raised {type(e).__name__} but should work")
        
        if mismatches:
            raise ImplementationStatusMismatch(
                f"{component_name} (status: {status}) has implementation mismatches:\n" +
                "\n".join(f"- {mismatch}" for mismatch in mismatches)
            )


def create_cop_testing_subclass(annotation_cls: Type[COPAnnotation], mixin_cls: Type[COPAnnotationTestingMixin]):
    """
    Create a testing-enhanced subclass of a COP annotation.
    
    Args:
        annotation_cls: The core annotation class to enhance
        mixin_cls: The testing mixin to apply
        
    Returns:
        A subclass with testing capabilities
    """
    testing_cls = type(f"{annotation_cls.__name__}", (annotation_cls, mixin_cls), {})
    
    # Wrap it to preserve signature and docstring
    @functools.wraps(annotation_cls)
    def testing_annotation(*args, **kwargs):
        return testing_cls(*args, **kwargs)
    
    return testing_annotation


# Create testing-enhanced versions of core annotations
intent = create_cop_testing_subclass(core_intent, COPAnnotationIntentTestingMixin)
implementation_status = create_cop_testing_subclass(core_implementation_status, COPAnnotationImplementationStatusTestingMixin)
risk = create_cop_testing_subclass(core_risk, COPAnnotationRiskTestingMixin)
invariant = create_cop_testing_subclass(core_invariant, COPAnnotationInvariantTestingMixin)
decision = create_cop_testing_subclass(core_decision, COPAnnotationDecisionTestingMixin)


# Helper functions for test tracking
def _record_test_verification(test_func, verification_info):
    """Record that a test verified a specific annotation."""
    # Implementation would store this information in a registry
    from .verification import register_test_verification
    register_test_verification(test_func, verification_info)


def _record_verification_failure(annotation_type, args, kwargs, exception):
    """Record a verification failure."""
    # Implementation would store information about the failure
    from .verification import register_verification_failure
    register_verification_failure(annotation_type, args, kwargs, exception)
