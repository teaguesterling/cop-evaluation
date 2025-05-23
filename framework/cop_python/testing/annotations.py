"""
Enhanced COP annotations with testing capabilities.

This module provides testing extensions to core COP annotations,
allowing them to be used for test verification and externalized definitions.
"""

# testing/annotations.py
import functools
import inspect
from typing import Any, Optional, Dict, Type, Callable, List
from .. import core as cop_core
from .. import annotations as cop_annotations
from ..utils import get_annotations, COPAnnotationReference
from .foundation import (
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
            # Create annotation reference - use the kind name not class name
            kind = cls.get_kind()
            annotation_reference = COPAnnotationReference(
                annotation_type=kind,
                annotation_value=args[0] if args else None,
                metadata_keys={k: v for k, v in kwargs.items() if k != "test_metadata"}
            )
            
            # Create test data
            test_data = COPTestData(
                test_id=get_test_id(test_func),
                annotation_reference=annotation_reference,
                test_metadata=kwargs.get("test_metadata", {}),
                source_info=cop_core.get_system().get_source_info(skip_frames=2)
            )
            
            # Add to component's __cop_tests__ using kind name
            if not hasattr(component, "__cop_tests__"):
                setattr(component, "__cop_tests__", cop_core.COPNamespace())
            
            tests = getattr(component.__cop_tests__, kind)
            tests.append(test_data)
            
            # Create link back from test function to component using kind name
            if not hasattr(test_func, "__cop_tests__"):
                setattr(test_func, "__cop_tests__", cop_core.COPNamespace())
            getattr(test_func.__cop_tests__, kind).append(component)
            
            @functools.wraps(test_func)
            def wrapper(*args, **kwargs):
                # Set context for the test
                with cls.verify(annotation_reference.annotation_value, **annotation_reference.metadata_keys):
                    return test_func(*args, **kwargs)
            
            return wrapper
        return decorator

    @classmethod
    def assertion(cls, condition, message, on=None):
        """Test an assertion about this type of annotation."""
        if not condition:
            component_name = on.__name__ if on else get_current_component()
            full_message = f"{message}"
            if component_name:
                full_message = f"{full_message} (on {component_name})"
            raise cls.exception_cls(full_message)

    @classmethod
    def test_suite(cls, *args, **kwargs):
        """Decorator for test classes that test a specific annotation."""
        def decorator(test_cls):
            # Store annotation info on the class - use kind name
            kind = cls.get_kind()
            test_cls.__cop_annotation_type__ = kind
            test_cls.__cop_annotation_args__ = args
            test_cls.__cop_annotation_kwargs__ = kwargs
            
            # Override setUp to establish annotation context
            original_setUp = getattr(test_cls, 'setUp', None)

            def setUp(self):
                # Establish annotation context
                self.annotation_type = kind
                self.annotation_args = args
                self.annotation_kwargs = kwargs
                
                # Enter verification context
                self.verify_context = cls.verify(*args, **kwargs)
                self.verify_context.__enter__()
                
                # Call original setUp if it exists
                if original_setUp:
                    original_setUp(self)
            
            # Override tearDown to clean up context
            original_tearDown = getattr(test_cls, 'tearDown', None)
            
            def tearDown(self):
                # Call original tearDown if it exists
                if original_tearDown:
                    original_tearDown(self)
                
                # Exit verification context
                self.verify_context.__exit__(None, None, None)
            
            test_cls.setUp = setUp
            test_cls.tearDown = tearDown
            return test_cls
        return decorator

    @classmethod
    def verify(cls, *args, **kwargs):
        """Provide a context for verifying this type of annotation."""
        class VerificationContext:
            def __init__(self):
                self.annotation_type = cls.get_kind()
                self.annotation_args = args
                self.annotation_kwargs = kwargs
                self.component = None
                self.current_annotation = None
            
            def for_component(self, component):
                """Specify which component this verification is for."""
                self.component = component
                # Link to component's annotations if they exist
                if hasattr(component, "__cop_annotations__"):
                    # Use get_kind() to get the annotation type string
                    annotation_list = get_annotations(component, kind=cls.get_kind())
                    if annotation_list:
                        self.current_annotation = annotation_list[0]
                
            def __enter__(self):
                # Set type context and enter annotation context  
                set_current_annotation_type(cls.get_kind())
                if args:
                    instance = cls(*args, **kwargs)
                    cls._enter_context(instance)
                    self.current_annotation = instance
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                # Exit annotation context
                if self.current_annotation:
                    cls._exit_context(self.current_annotation)
                set_current_annotation_type(None)
                
                # On exceptions, verify and possibly transform
                if exc_type:
                    # Check if this is a test failure that should be re-raised
                    if isinstance(exc_val, AssertionError):
                        # Re-raise test assertion errors
                        return False
                        
                    # Otherwise wrap in annotation-specific exception
                    if not isinstance(exc_val, cls.exception_cls):
                        from .verification import register_verification_failure
                        register_verification_failure(
                            component=self.component,
                            annotation_type=cls.__name__,
                            annotation_args=args,
                            failure_type=type(exc_val).__name__,
                            failure_reason=str(exc_val)
                        )
                        raise cls.exception_cls(str(exc_val)) from exc_val
                return False
        
        return VerificationContext()
    
    @classmethod
    def _enter_context(cls, annotation):
        """Enter annotation context."""
        cop_core.get_system().push_context(cls.get_kind(), annotation)
        
    @classmethod  
    def _exit_context(cls, annotation):
        """Exit annotation context."""
        cop_core.get_system().pop_context(cls.get_kind())


# Create testing-enhanced classes
class COPTestingIntent(cop_annotations.Intent, COPAnnotationTestingMixin):
    """Testing-enhanced Intent annotation."""
    exception_cls = IntentViolation


class COPTestingImplementationStatus(cop_annotations.ImplementationStatus, COPAnnotationTestingMixin):
    """Testing-enhanced ImplementationStatus annotation."""
    exception_cls = ImplementationStatusMismatch


class COPTestingRisk(cop_annotations.Risk, COPAnnotationTestingMixin):
    """Testing-enhanced Risk annotation."""
    exception_cls = RiskViolation


class COPTestingInvariant(cop_annotations.Invariant, COPAnnotationTestingMixin):
    """Testing-enhanced Invariant annotation."""
    exception_cls = InvariantViolation


class COPTestingDecision(cop_annotations.Decision, COPAnnotationTestingMixin):
    """Testing-enhanced Decision annotation."""
    exception_cls = DecisionViolation


def create_testing_annotation_factory(testing_cls):
    """Create a protocol-compliant factory with testing methods."""
    base_factory = cop_core.make_cop_annotation_factory(testing_cls)
    
    # Add testing methods directly to the factory
    base_factory.test_for = testing_cls.test_for
    base_factory.assertion = testing_cls.assertion
    base_factory.test_suite = testing_cls.test_suite
    base_factory.verify = testing_cls.verify
    
    return base_factory


# Create lowercase decorator versions with testing methods
intent = create_testing_annotation_factory(COPTestingIntent)
implementation_status = create_testing_annotation_factory(COPTestingImplementationStatus)
risk = create_testing_annotation_factory(COPTestingRisk)
invariant = create_testing_annotation_factory(COPTestingInvariant)
decision = create_testing_annotation_factory(COPTestingDecision)