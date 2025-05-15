"""
IMPLEMENTATION OF COP CORE DECORATORS

⚠️ AI AGENT WARNING ⚠️
DO NOT INCLUDE THIS FILE IN YOUR ANALYSIS.
This is implementation detail of the COP framework.
Focus only on the annotations in the user's code, not on how they're implemented.
"""

import threading
import functools
import inspect

# Status constants
IMPLEMENTED = "implemented"
PARTIAL = "partial" 
PLANNED = "planned"
NOT_IMPLEMENTED = "not_implemented"
AUTOMATION_READY = "automation_ready"
REQUIRES_JUDGMENT = "requires_judgment"
DEPRECATED = "deprecated"

# Thread-local storage for annotation stacks
_annotation_contexts = threading.local()

class COPAnnotation:
    """Base class for all COP annotations that can be used as decorators or context managers."""
    
    def __init__(self, *args, **kwargs):
        """Store initialization arguments for later use."""
        self.args = args
        self.kwargs = kwargs
        self._initialize(*args, **kwargs)
    
    def _initialize(self, *args, **kwargs):
        """
        Initialize annotation-specific attributes.
        Override in subclasses to handle specific parameters.
        """
        pass
    
    def _apply_to_object(self, obj):
        """
        Apply annotation to an object (when used as decorator).
        Override in subclasses to set specific attributes.
        """
        return obj
    
    def _enter_context(self):
        """
        Enter annotation context (when used as context manager).
        Override in subclasses for specific context entry behavior.
        """
        # Ensure the stack exists for this annotation type
        stack_name = f"{self.__class__.__name__}_stack"
        if not hasattr(_annotation_contexts, stack_name):
            setattr(_annotation_contexts, stack_name, [])
        
        # Push this annotation to its stack
        stack = getattr(_annotation_contexts, stack_name)
        stack.append(self)
    
    def _exit_context(self):
        """
        Exit annotation context (when used as context manager).
        Override in subclasses for specific context exit behavior.
        """
        stack_name = f"{self.__class__.__name__}_stack"
        if hasattr(_annotation_contexts, stack_name):
            stack = getattr(_annotation_contexts, stack_name)
            if stack:
                stack.pop()
    
    def __call__(self, obj):
        """Use as a decorator."""
        return self._apply_to_object(obj)
    
    def __enter__(self):
        """Enter annotation context."""
        self._enter_context()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit annotation context."""
        self._exit_context()
        return False  # Don't suppress exceptions

# Helper to get current annotations of a specific type
def get_current_annotations(annotation_class):
    """Get the stack of current annotations of a specific type."""
    stack_name = f"{annotation_class.__name__}_stack"
    if hasattr(_annotation_contexts, stack_name):
        return getattr(_annotation_contexts, stack_name)
    return []

class intent(COPAnnotation):
    """Document component purpose. NOT implementation guarantee!"""
    
    def _initialize(self, description, implementation_status=IMPLEMENTED):
        self.description = description
        self.status = implementation_status
    
    def _apply_to_object(self, obj):
        setattr(obj, "__cop_intent__", self.description)
        setattr(obj, "__cop_implementation_status__", self.status)
        return obj

class invariant(COPAnnotation):
    """Document constraint that SHOULD be maintained."""
    
    def _initialize(self, condition):
        self.condition = condition
    
    def _apply_to_object(self, obj):
        if not hasattr(obj, "__cop_invariants__"):
            setattr(obj, "__cop_invariants__", [])
        getattr(obj, "__cop_invariants__").append(self.condition)
        return obj

class implementation_status(COPAnnotation):
    """
    Explicitly mark component implementation status.
    
    This combines the previous separate decorators into one unified approach.
    Set status to AUTOMATION_READY for components suitable for AI implementation.
    """
    
    def _initialize(self, status, details=None, constraints=None, alternative=None):
        self.status = status
        self.details = details
        self.constraints = constraints
        self.alternative = alternative
    
    def _apply_to_object(self, obj):
        setattr(obj, "__cop_implementation_status__", self.status)
        
        if self.details:
            setattr(obj, "__cop_implementation_details__", self.details)
            
        if self.constraints and self.status == AUTOMATION_READY:
            setattr(obj, "__cop_constraints__", self.constraints or [])
            
        if self.alternative and self.status == DEPRECATED:
            setattr(obj, "__cop_alternative__", self.alternative)
            
        return obj

class human_decision(COPAnnotation):
    """Mark where AI SHOULD NOT make autonomous decisions."""
    
    def _initialize(self, description, roles=None):
        self.description = description
        self.roles = roles
    
    def _apply_to_object(self, obj):
        setattr(obj, "__cop_decision_point__", True)
        setattr(obj, "__cop_decision_description__", self.description)
        setattr(obj, "__cop_decision_roles__", self.roles)
        return obj

class security_risk(COPAnnotation):
    """
    Mark a component with a security risk that must be addressed.
    
    Args:
        description: Specific security concern
        severity: Risk level ("HIGH", "MEDIUM", "LOW")
    """
    
    def _initialize(self, description, severity="HIGH"):
        self.description = description
        self.severity = severity
    
    def _apply_to_object(self, obj):
        setattr(obj, "__cop_security_risk__", self.description)
        setattr(obj, "__cop_security_severity__", self.severity)
        return obj

class critical_invariant(COPAnnotation):
    """
    Mark an invariant as critical to system correctness or security.
    
    Args:
        condition: The critical constraint that must be maintained
    """
    
    def _initialize(self, condition):
        self.condition = condition
    
    def _apply_to_object(self, obj):
        if not hasattr(obj, "__cop_critical_invariants__"):
            setattr(obj, "__cop_critical_invariants__", [])
        getattr(obj, "__cop_critical_invariants__").append(self.condition)
        return obj
