"""
Enhanced COP annotations with testing capabilities.

This module provides testing extensions to core COP annotations,
allowing them to be used for test verification and externalized definitions.
"""

# testing/annotations.py
import functools
import inspect
from typing import Any, Optional, Dict, Type, Callable, List
from .. import core
from ..utils import get_annotations, COPAnnotationReference
from .core import (
    COPTestData, get_test_id, set_current_annotation_type, 
    get_current_component, COPAnnotationViolation,
    InvariantViolation, RiskViolation, ImplementationStatusMismatch,
    DecisionViolation, IntentViolation
)
    

class COPAnnotationTestingMixin:
    """Mixin that adds testing capabilities to COP annotations."""

    exception_cls = COPAnnotationViolation
    
    @classmethod
    def test_for(cls, component, *args, **kwargs):
        """Create a test decorator that verifies this type of annotation on a specific component."""
        def decorator(test_func):
            # Create annotation reference
            annotation_reference = COPAnnotationReference(
                annotation_type=cls.__name__,
                annotation_value=args[0] if args else None,
                metadata_keys={k: v for k, v in kwargs.items() if k != "test_metadata"}
            )
            
            # Create test data
            test_data = COPTestData(
                test_id=get_test_id(test_func),
                annotation_reference=annotation_reference,
                test_metadata=kwargs.get("test_metadata", {}),
                source_info=core._cop_system.get_source_info()
            )
            
            # Add to component's __cop_tests__
            if not hasattr(component, "__cop_tests__"):
                setattr(component, "__cop_tests__", core.COPNamespace())
            
            # Get list for this annotation type
            tests_list = getattr(component.__cop_tests__, cls.__name__)
            tests_list.append(test_data)
            
            # Link component back to test function
            setattr(test_func, f"__cop_tests_{cls.__name__}__", component)
            
            @functools.wraps(test_func)
            def wrapper(*test_args, **test_kwargs):
                # Run the test
                result = test_func(*test_args, **test_kwargs)
                
                # Record test execution
                from .verification import register_test_execution
                register_test_execution(test_func, component, cls.__name__)
                
                return result
            
            return wrapper
        
        return decorator
        
    @classmethod
    def assertion(cls, condition: bool, message: Optional[str] = None, *, on: Any = None) -> None:
        """Assert that a condition related to this annotation type is true."""
        if not condition:
            # Build the error message
            error_message = message or f"{cls.__name__.title()} violation"
            
            if on:
                component_name = getattr(on, "__name__", str(on))
                error_message = f"{error_message} on {component_name}"
            
            # Get the appropriate exception class
            exception_class = cls.exception_cls
            
            # Raise the exception
            raise exception_class(error_message)
    
    @classmethod
    def test_suite(cls, *args, **kwargs):
        """Create a test suite for this annotation type."""
        def decorator(test_class):
            # Store annotation type info on the class
            test_class.__cop_annotation_type__ = cls.__name__
            test_class.__cop_annotation_args__ = args
            test_class.__cop_annotation_kwargs__ = kwargs
            
            # Process test methods
            for name, method in inspect.getmembers(test_class, predicate=inspect.isfunction):
                if name.startswith("test_"):
                    # If no explicit annotation, add default annotation from the suite
                    if not any(hasattr(method, attr) for attr in 
                              [f"__cop_tests_{cls.__name__}__", f"__cop_verifies_{cls.__name__}__"]):
                        # Apply the class-level annotation parameters
                        setattr(method, f"__cop_verifies_{cls.__name__}__", {
                            "args": args,
                            "kwargs": kwargs
                        })
            
            # Wrap setUp to set annotation context
            original_setUp = getattr(test_class, "setUp", None)
            
            def setUp(self):
                if original_setUp:
                    original_setUp(self)
                
                # Set annotation type context
                set_current_annotation_type(cls.__name__)
                
                # Make current component and annotation info available
                component = get_current_component()
                if component:
                    self.component = component
                
                self.annotation_type = cls.__name__
                self.annotation_args = args
                self.annotation_kwargs = kwargs
            
            # Set the setUp method
            test_class.setUp = setUp
            
            # Similar tearDown implementation to clear context
            
            return test_class
        
        return decorator
    
    @classmethod
    def verify(cls, *args, **kwargs):
        """Create a context manager for verifying an annotation during a test."""
        # Create the annotation
        annotation = cls(*args, **kwargs)
        
        # The context manager will track when this annotation is active
        class VerificationContext:
            def __init__(self):
                self.component = None
            
            def for_component(self, component):
                """Specify the component being verified."""
                self.component = component
                return self
            
            def __enter__(self):
                cls._enter_context(annotation)
                return self
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                # Check if the verification was successful
                if exc_type is not None:
                    # An exception occurred - check if it's a test assertion
                    if issubclass(exc_type, AssertionError):
                        # Record the verification failure
                        from .verification import register_verification_failure
                        register_verification_failure(cls.__name__, args, kwargs, exc_val)
                
                cls._exit_context(annotation)
                return False  # Don't suppress exceptions
        
        return VerificationContext()
    
    @classmethod
    def _enter_context(cls, annotation):
        """Enter annotation context."""
        core._cop_system.push_context(cls.__name__, annotation)
    
    @classmethod
    def _exit_context(cls, annotation):
        """Exit annotation context."""
        core._cop_system.pop_context(cls.__name__)


def create_cop_testing_subclass(annotation_cls: Type[core.COPAnnotation], exception_cls: Type[core.COPAnnotationViolation]):
    """Create a testing-enhanced subclass of a COP annotation."""
    testing_cls = type(
        f"{annotation_cls.__name__}", 
        (annotation_cls, COPAnnotationTestingMixin), {
            "exception_cls": exception_cls
        }
    )
    
    # Wrap it to preserve signature and docstring
    @functools.wraps(annotation_cls)
    def testing_annotation(*args, **kwargs):
        return testing_cls(*args, **kwargs)
    
    # Add all class methods from the enhanced class
    for name, method in inspect.getmembers(testing_cls, predicate=inspect.ismethod):
        if name.startswith('_'):
            continue
        setattr(testing_annotation, name, method)
    
    return testing_annotation

# Create testing-enhanced versions of core annotations
intent = create_cop_testing_subclass(core.intent, IntentViolation)
implementation_status = create_cop_testing_subclass(core.implementation_status, ImplementationStatusMismatch)
risk = create_cop_testing_subclass(core.risk, RiskViolation)
invariant = create_cop_testing_subclass(core.invariant, InvariantViolation)
decision = create_cop_testing_subclass(core.decision, DecisionViolation)
