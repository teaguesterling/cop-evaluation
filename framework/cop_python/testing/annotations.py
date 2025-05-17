"""
Enhanced COP annotations with testing capabilities.

This module provides testing extensions to core COP annotations,
allowing them to be used for test verification and externalized definitions.
"""

import functools
import inspect
import threading
import types
from typing import Any, Optional, Dict, List, NamedTuple, Type, Callable, Union
from .. import core
from ..utils import get_annotations

# Thread-local for tracking current test context
_test_context = threading.local()

def set_current_component(component):
    """Set current component being tested."""
    _test_context.current_component = component

def get_current_component():
    """Get current component being tested."""
    return getattr(_test_context, "current_component", None)

def set_current_annotation_type(annotation_type):
    """Set current annotation type being tested."""
    _test_context.current_annotation_type = annotation_type

def get_current_annotation_type():
    """Get current annotation type being tested."""
    return getattr(_test_context, "current_annotation_type", None)

## Test Data

class COPTestData(NamedTuple):
    """Structured representation of a COP test."""
    test_id: str                                    # Fully qualified test identifier (module.class.method)
    anootation: Optional[COPAnnotationData] = None  # The COP annotation being tested
    test_metadata: Optional[Dict[str, Any]] = None  # Test-specific metadata
    externalized: bool = False                      # Whether test link was defined outside component
    last_run: Optional[str] = None                  # Timestamp of last execution
    result: Optional[str] = None                    # Result of last execution (PASS/FAIL)
    source_info: Optional[Any] = None               # Source location information
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert test data to dictionary format for serialization."""
        result = self._asdict()
        if self.source_info:
            result["source_info"] = self.source_info._asdict()
        return result


def _add_test_record(component, test_func, annotation_type, annotation_value=None, annotation_metadata=None, test_metadata=None, externalized=False):
    """
    Add a test record to a component's __cop_tests__ structure.
    
    Args:
        component: The component being tested
        test_func: The test function
        annotation_type: Type of annotation being tested (e.g., "risk", "invariant")
        annotation_value: Value of the annotation being tested
        annotation_metadata: Additional annotation metadata
        test_metadata: Test-specific metadata
        externalized: Whether the test link was defined outside the component
        
    Returns:
        COPTestData object representing the created test record
    """
    # Get module and name info for test identification
    module_name = test_func.__module__
    func_name = test_func.__name__
    
    # Handle class methods by checking for class attribute
    if hasattr(test_func, "__self__") and test_func.__self__ is not None:
        class_name = test_func.__self__.__class__.__name__
        test_id = f"{module_name}.{class_name}.{func_name}"
    else:
        test_id = f"{module_name}.{func_name}"
    # Create test record
    test_record = COPTestData(
        test_id=test_id,
        annotation_value=annotation_value,
        annotation_metadata=annotation_metadata or {},
        test_metadata=test_metadata or {},
        externalized=externalized,
        last_run=None,
        result=None
    )
    # Get list for this annotation type
    tests_list _get_or_create_tests(component)[annotation_type]
    tests_list.append(test_record)
    return test_record


## Verification Data

class COPTestVerification(NamedTuple):
    """Structured representation of what a test verifies."""
    component: Any                         # Component being tested
    component_name: str                    # Component name for reference
    annotation_type: str                   # Type of annotation being tested
    annotation_value: Optional[str] = None  # Value of the annotation being tested
    annotation_metadata: Optional[Dict[str, Any]] = None  # Annotation properties
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = self._asdict()
        # Remove the actual component object for serialization
        result.pop("component", None)
        return result

# Helper functions for test information
def _get_or_create_tests(test_func_or_class):
    """Get or create the test info namespace for a test function or class."""
    if not hasattr(test_func_or_class, "__cop_tests__"):
        test_info = COPNamespace(verifications=[], metadata={})
        setattr(test_func_or_class, "__cop_tests__", test_info)
    return getattr(test_func_or_class, "__cop_tests__")

def _get_test_namespace(test_func_or_class):
    """Get or create the test info namespace for a test function or class."""
    if hasattr(test_func_or_class, "__cop_tests__"):
        return getattr(test_func_or_class, "__cop_tests__")
    else:
        return COPNamespace(verifications=[], metadata={})


# Use utility functions for test info operations
def _get_or_create_test_info(test_func_or_class):
    """Get or create the test info namespace for a test function or class."""
    if not hasattr(test_func_or_class, "__cop_test_info__"):
        test_info = COPNamespace(verifications=[], metadata={})
        setattr(test_func_or_class, "__cop_test_info__", test_info)
    return getattr(test_func_or_class, "__cop_test_info__")


def _add_verification(test_info, component, annotation_type, annotation_value=None, annotation_metadata=None):
    """Add a verification entry to a test info namespace."""
    component_name = getattr(component, "__name__", str(component))    
    verification = COPTestVerification(
        component=component,
        component_name=component_name,
        annotation_type=annotation_type,
        annotation_value=annotation_value,
        annotation_metadata=annotation_metadata or {}
    )
    test_info.verifications.append(verification)
    return verification


def _get_verifications(test_info, component=None, component_name=None, annotation_type=None):
    """Get verifications from a test info namespace, filtered by component and/or annotation type."""
    if not hasattr(test_info, "verifications"):
        return []
        
    result = test_info.verifications
    if component:
        result = [v for v in result if v.component is component]
    if component_name:
        result = [v for v in result if v.component_name == component_name]
    if annotation_type:
        result = [v for v in result if v.annotation_type == annotation_type]
    
    return result


def _record_test_execution(test_func, component, annotation_type):
    """Record that a test was executed."""
    # Implementation would store execution information
    # This could update the last_run and result fields of the test record
    from .verification import register_test_execution
    register_test_execution(test_func, component, annotation_type)


def _record_verification_failure(annotation_type, args, kwargs, exception):
    """Record a verification failure."""
    # Implementation would store information about the failure
    from .verification import register_verification_failure
    register_verification_failure(annotation_type, args, kwargs, exception)


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
        annotation_type = cls.kind
        annotation_value = args[0] if args else None
        
        def decorator(test_func):
            # Get or create test info
            test_info = _get_or_create_test_info(test_func)            
            # Add verification
            test_info.add_verification(
                component=component,
                annotation_type=annotation_type,
                annotation_value=annotation_value,
                annotation_metadata=kwargs
            )
            # Add test record to component
            _add_test_record(
                component=component,
                test_func=test_func,
                annotation_type=annotation_type,
                annotation_value=annotation_value,
                annotation_metadata=kwargs,
                externalized=False
            )
            @functools.wraps(test_func)
            def wrapper(*test_args, **test_kwargs):
                result = test_func(*test_args, **test_kwargs)
                _record_test_execution(test_func, component, annotation_type)
                return result
            return wrapper
        return decorator
    
    @classmethod
    def test(cls, *args, **kwargs):
        """
        Test decorator that retrieves component from context.
        
        This decorator is used within a test class decorated with @tests_component.
        
        Args:
            *args, **kwargs: Arguments matching the annotation being tested
            
        Returns:
            A decorator function for test methods
        """
        annotation_type = cls.kind
        annotation_value = args[0] if args else None
        
        def decorator(test_func):
            # Get or create test info
            test_info = _get_or_create_test_info(test_func)
            
            @functools.wraps(test_func)
            def wrapper(self, *test_args, **test_kwargs):
                # Get component from self or context
                component = getattr(self, "component", get_current_component())
                if component:
                    # Add verification to test info
                    test_info.add_verification(
                        component=component,
                        annotation_type=annotation_type,
                        annotation_value=annotation_value,
                        annotation_metadata=kwargs
                    )
                    # Add test record to component
                    _add_test_record(
                        component=component,
                        test_func=test_func,
                        annotation_type=annotation_type,
                        annotation_value=annotation_value,
                        annotation_metadata=kwargs,
                        externalized=False
                    )
                    # Record test execution
                    _record_test_execution(test_func, component, annotation_type)
                
                # Run the test
                return test_func(self, *test_args, **test_kwargs)
            return wrapper
        return decorator
    
    @classmethod
    def test_suite(cls, *args, **kwargs):
        """
        Create a test suite for this annotation type.
        
        Args:
            *args, **kwargs: Arguments for filtering or categorizing tests
            
        Returns:
            A decorator function for test classes
        """
        annotation_type = cls.__name__
        def decorator(test_class):
            # Store annotation type info on the class
            test_info = _get_or_create_test_info(test_class)
            test_info.annotation_type = annotation_type
            test_info.annotation_args = args
            test_info.annotation_kwargs = kwargs
            # Wrap setUp method to set context
            original_setUp = getattr(test_class, "setUp", None)
            def setUp(self):
                if original_setUp:
                    original_setUp(self)
                # Set annotation type context
                set_current_annotation_type(annotation_type)
                # Make annotation parameters available
                self.annotation_type = annotation_type
                self.annotation_args = args
                self.annotation_kwargs = kwargs
                # Get component from parent class if available
                parent_class = self.__class__
                while parent_class:
                    if hasattr(parent_class, "__cop_test_info__"):
                        parent_info = getattr(parent_class, "__cop_test_info__")
                        for v in parent_info.verifies:
                            if v.component:
                                self.component = v.component
                                break
                    # Try parent class
                    parent_class = parent_class.__base__
                    if parent_class is object:
                        break
            # Set the setUp method
            test_class.setUp = setUp
            # Wrap tearDown to clear context
            original_tearDown = getattr(test_class, "tearDown", None)
            
            def tearDown(self):
                if original_tearDown:
                    original_tearDown(self)
                # Clear annotation type context
                set_current_annotation_type(None)
            # Set the tearDown method
            test_class.tearDown = tearDown
            return test_class
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
        annotations = get_annotations(component)
        anno_type = cls.kind
        
        if hasattr(annotations, anno_type):
            anno_list = getattr(annotations, anno_type)
            
            # Mark the most recently added annotation
            if anno_list and hasattr(anno_list[-1], "metadata"):
                metadata = anno_list[-1].metadata or {}
                metadata["externalized"] = True
        
        return component
    
    @classmethod
    def verify(cls, *args, **kwargs):
        """
        Create a context manager for verifying an annotation during a test.
        
        Args:
            *args, **kwargs: Arguments matching the annotation being tested
            
        Returns:
            A context manager for verification
        """
        annotation_type = cls.kind
        annotation_value = args[0] if args else None
        
        class VerificationContext:
            def __init__(self):
                self.component = None
            
            def for_component(self, component):
                """Specify the component being verified."""
                self.component = component
                return self
                
            def __enter__(self):
                # Save current contexts
                self.prev_annotation_type = get_current_annotation_type()
                
                # Set context
                set_current_annotation_type(annotation_type)
                
                # If component is explicitly specified, record it
                if self.component is None:
                    self.component = get_current_component()
                
                # If we have a component, try to record test info
                if self.component:
                    # Get current test function frame
                    frame = inspect.currentframe().f_back
                    
                    # Try to find the test function
                    while frame:
                        if frame.f_code.co_name.startswith('test_'):
                            # Found test function
                            function_name = frame.f_code.co_name
                            module_name = frame.f_globals.get('__name__', '')
                            
                            # Create a proxy function object to use with _add_test_record
                            test_func = types.SimpleNamespace()
                            test_func.__name__ = function_name
                            test_func.__module__ = module_name
                            
                            # Add test record
                            _add_test_record(
                                component=self.component,
                                test_func=test_func,
                                annotation_type=annotation_type,
                                annotation_value=annotation_value,
                                annotation_metadata=kwargs,
                                externalized=True
                            )
                            
                            break
                        
                        frame = frame.f_back
                
                return self
                    
            def __exit__(self, exc_type, exc_val, exc_tb):
                # Restore previous context
                set_current_annotation_type(self.prev_annotation_type)
                
                # Check for verification failure
                if exc_type is not None and issubclass(exc_type, AssertionError):
                    _record_verification_failure(annotation_type, args, kwargs, exc_val)
                
                return False  # Don't suppress exceptions
        
        return VerificationContext()


class testing_component:
    """
    Context manager for testing a specific component.
    
    Example:
        with testing_component(process_payment):
            # Test code that has access to the component
            with invariant.verify("Transactions must be atomic"):
                # Test code that verifies the invariant
    """
    
    def __init__(self, component):
        """
        Initialize with a component to test.
        
        Args:
            component: The component to test
        """
        self.component = component
        self.previous_component = None
    
    def __enter__(self):
        """
        Enter the testing context.
        
        Returns:
            The component being tested
        """
        # Store the current component
        self.previous_component = get_current_component()
        
        # Set the new component
        set_current_component(self.component)
        
        return self.component
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        Exit the testing context.
        
        Args:
            exc_type: Exception type if an exception was raised, else None
            exc_value: Exception value if an exception was raised, else None
            traceback: Exception traceback if an exception was raised, else None
            
        Returns:
            False: Don't suppress exceptions
        """
        # Restore the previous component
        set_current_component(self.previous_component)
        
        return False  # Don't suppress exceptions


class tests_component:
    """
    Decorator for creating component test classes.
    
    Example:
        @tests_component(process_payment)
        class ProcessPaymentTests:
            # All test methods have access to self.component
    """
    
    def __init__(self, component, **kwargs):
        """
        Initialize with the component to test.
        
        Args:
            component: The component to test
            **kwargs: Additional metadata for reporting
        """
        self.component = component
        self.metadata = kwargs
    
    def __call__(self, cls):
        """
        Apply the decorator to a class.
        
        Args:
            cls: The class to decorate
            
        Returns:
            The decorated class
        """
        # Add test info to class
        test_info = _get_or_create_test_info(cls)
        test_info.add_verification(
            component=self.component,
            annotation_type="component_test",
            annotation_value=None,
            annotation_metadata=self.metadata
        )
        
        # Wrap setUp to set component context
        original_setUp = getattr(cls, "setUp", None)
        
        def setUp(self):
            # Call original setUp if it exists
            if original_setUp:
                original_setUp(self)
            
            # Set component context
            set_current_component(self.component)
            
            # Make component available to test methods
            self.component = self.component
        
        # Wrap tearDown to clear context
        original_tearDown = getattr(cls, "tearDown", None)
        
        def tearDown(self):
            # Call original tearDown if it exists
            if original_tearDown:
                original_tearDown(self)
            
            # Clear component context
            set_current_component(None)
        
        # Set methods
        cls.setUp = setUp
        cls.tearDown = tearDown
        
        # Process inner classes for annotation types
        for name, inner_cls in cls.__dict__.items():
            if isinstance(inner_cls, type):
                # Add test info to inner class
                inner_test_info = _get_or_create_test_info(inner_cls)
                inner_test_info.add_verification(
                    component=self.component,
                    annotation_type="component_test",
                    annotation_value=None,
                    annotation_metadata={}
                )
                
                # If the class name indicates an annotation type, link it
                for anno_type in ["risk", "invariant", "decision", "intent", "implementation_status"]:
                    if name.lower() == f"{anno_type}tests":
                        inner_test_info.annotation_type = anno_type
        
        return cls


def create_cop_testing_subclass(annotation_cls):
    """
    Create a testing-enhanced subclass of a COP annotation.
    
    Args:
        annotation_cls: The core annotation class to enhance
        
    Returns:
        A subclass with testing capabilities
    """
    class_name = annotation_cls.kind
    
    # Create the enhanced class
    testing_cls = type(class_name, (annotation_cls, COPAnnotationTestingMixin), {})
    
    # Wrap it to preserve signature and docstring
    @functools.wraps(annotation_cls)
    def testing_annotation(*args, **kwargs):
        return testing_cls(*args, **kwargs)
    
    # Add class methods from the enhanced class
    for name, method in inspect.getmembers(testing_cls, predicate=inspect.ismethod):
        if name.startswith('_'):
            continue
        setattr(testing_annotation, name, method)
    
    return testing_annotation


# Create testing-enhanced versions of core annotations
intent = create_cop_testing_subclass(core.intent)
implementation_status = create_cop_testing_subclass(core.implementation_status)
risk = create_cop_testing_subclass(core.risk)
invariant = create_cop_testing_subclass(core.invariant)
decision = create_cop_testing_subclass(core.decision)
