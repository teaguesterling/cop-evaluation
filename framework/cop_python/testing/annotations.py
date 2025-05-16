# cop_python/testing/annotations.py
import functools
from ..core import (
    COPAnnotation, 
    intent as core_intent,
    implementation_status as core_implementation_status,
    risk as core_risk,
    invariant as core_invariant,
    decision as core_decision
)

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


def create_cop_testing_subclass(annotation_cls):
    """
    Create a testing-enhanced subclass of a COP annotation.
    
    Args:
        annotation_cls: The core annotation class to enhance
        
    Returns:
        A subclass with testing capabilities
    """
    testing_cls = type(
        f"{annotation_cls.__name__}",  # Keep the same name for seamless usage
        (annotation_cls, COPAnnotationTestingMixin), 
        {}
    )
    
    # Wrap it to preserve signature and docstring
    @functools.wraps(annotation_cls)
    def testing_annotation(*args, **kwargs):
        return testing_cls(*args, **kwargs)
    
    return testing_annotation


# Create testing-enhanced versions of core annotations
intent = create_cop_testing_subclass(core_intent)
implementation_status = create_cop_testing_subclass(core_implementation_status)
risk = create_cop_testing_subclass(core_risk)
invariant = create_cop_testing_subclass(core_invariant)
decision = create_cop_testing_subclass(core_decision)


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
