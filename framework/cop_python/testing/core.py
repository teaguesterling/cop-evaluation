# testing/core.py

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

# Context tracking mechanism
_test_context = threading.local()

def set_current_component(component):
    """Set the current component being tested."""
    _test_context.current_component = component

def get_current_component():
    """Get the current component being tested."""
    return getattr(_test_context, "current_component", None)

def set_current_annotation_type(annotation_type):
    """Set the current annotation type being tested."""
    _test_context.current_annotation_type = annotation_type

def get_current_annotation_type():
    """Get the current annotation type being tested."""
    return getattr(_test_context, "current_annotation_type", None)

# Component testing context manager
class testing_component:
    """Context manager for testing a specific component."""
    
    def __init__(self, component):
        self.component = component
        self.previous_component = None
    
    def __enter__(self):
        self.previous_component = get_current_component()
        set_current_component(self.component)
        return self.component
    
    def __exit__(self, exc_type, exc_value, traceback):
        set_current_component(self.previous_component)
        return False

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

# Utility functions
def get_test_id(test_func):
    """Generate a fully qualified test ID."""
    module_name = test_func.__module__
    func_name = test_func.__name__
    
    # Handle class methods
    if hasattr(test_func, "__self__") and test_func.__self__ is not None:
        class_name = test_func.__self__.__class__.__name__
        return f"{module_name}.{class_name}.{func_name}"
    
    return f"{module_name}.{func_name}"

def get_current_context():
    """Get the current annotation context."""
    context = {}
    for annotation_type in ["invariant", "risk", "implementation_status", "decision", "intent"]:
        if hasattr(_test_context, f"{annotation_type}_stack"):
            stack = getattr(_test_context, f"{annotation_type}_stack")
            if stack:
                context[annotation_type] = stack[-1]
    return context
