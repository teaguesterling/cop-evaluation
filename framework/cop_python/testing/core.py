import functools
import inspect
import threading
from ..runtime import get_system
from ..utils import COPAnnotationReference


# Exception classes
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


# Test data structure
class COPTestData(NamedTuple):
    """Structured representation of a COP test."""
    test_id: str                                          # Fully qualified test identifier
    annotation_reference: COPAnnotationReference        # Reference to the annotation being tested
    test_metadata: Optional[Dict[str, Any]] = None        # Test-specific metadata
    source_info: Optional[SourceInfo] = None              # Source location information of the test
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert test data to dictionary format for serialization."""
        result = self._asdict()
        if self.source_info:
            result["source_info"] = self.source_info._asdict()
        return result
        

class tests_concept:
    """
    Context manager and decorator for testing a specific concept.
    
    Can be used in two ways:
    
    1. As a context manager:
       with tests_concept(process_payment):
           # Test code with access to process_payment
    
    2. As a decorator:
       @tests_concept(process_payment)
       def test_payment_flow():
           # Test code with implicit access to process_payment
           
       @tests_concept(process_payment)
       class TestPaymentProcessing:
           def test_basic_flow(self):
               # Test code with self.concept = process_payment
    """
    
    def __init__(self, component):
        """Initialize with the concept to test."""
        self.component = component
    
    def __enter__(self):
        """Enter the testing context."""
        get_system().push_context("test_concept", self.component)
        return self.component
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Exit the testing context."""
        get_system().pop_context("test_concept")
        return False
    
    def __call__(self, func_or_class):
        """
        Use as a decorator for a test function or class.
        
        Args:
            func_or_class: The function or class to decorate
            
        Returns:
            Decorated function or class
        """
        if inspect.isclass(func_or_class):
            # Decorating a test class
            return self._decorate_class(func_or_class)
        else:
            # Decorating a test function
            return self._decorate_function(func_or_class)
    
    def _decorate_function(self, func):
        """Decorate a test function to run with this concept."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with self:
                # For test functions, add concept as first parameter if needed
                sig = inspect.signature(func)
                if len(args) < len(sig.parameters) and not args:
                    # Function expects concept as first parameter
                    return func(self.concept, *args, **kwargs)
                return func(*args, **kwargs)
        
        # Store component reference on function for direct access
        wrapper.__cop_concept_component__ = self.component
        
        return wrapper
    
    def _decorate_class(self, cls):
        """Decorate a test class to run with this component."""
        # Store component on the class
        cls.__cop_concept_component__ = self.component
        
        # Add setup method to make component available to test methods
        original_setup = getattr(cls, "setUp", None)
        
        def setUp(self):
            # Call original setup if it exists
            if original_setup:
                original_setup(self)
            
            # Set component context
            get_system().push_context("test_component", cls.__cop_concept_component__)
            
            # Make component available to test methods
            self.concept = cls.__cop_concept_component__
        
        # Add teardown to clean up context
        original_teardown = getattr(cls, "tearDown", None)
        
        def tearDown(self):
            # Clean up component context
            get_system().pop_context("test_concept")
            
            # Call original teardown if it exists
            if original_teardown:
                original_teardown(self)
        
        # Set the methods
        cls.setUp = setUp
        cls.tearDown = tearDown
        
        return cls

# Utility functions

def get_current_concept():
    """Get the component currently being tested."""
    return get_system().get_current_context("test_concept")

def set_current_annotation_type(annotation_type):
    """Set the current annotation type being tested."""
    get_system().push_context("test_annotation_type", annotation_type)

def get_current_annotation_type():
    """Get the current annotation type being tested."""
    return get_system().get_current_context("test_annotation_type")
    

def get_test_id(test_func):
    """Generate a fully qualified test ID."""
    module_name = test_func.__module__
    func_name = test_func.__name__
    
    # Handle class methods
    if hasattr(test_func, "__self__") and test_func.__self__ is not None:
        class_name = test_func.__self__.__class__.__name__
        return f"{module_name}.{class_name}.{func_name}"
    
    return f"{module_name}.{func_name}"

