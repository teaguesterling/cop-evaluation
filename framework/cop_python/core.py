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
from typing import List, Dict, Any, Callable, Optional, Type, Union

# Status constants and hierarchy
IMPLEMENTED = "implemented"              # Implementation is complete and expected to be correct
REQUIRES_JUDGMENT = "requires_judgment"  # Human input required to change this code
BUGGY = "buggy"                          # Implementation is or was complete but has known bugs or failing tests
PARTIAL = "partial"                      # Implementation is incomplete but has begun
AUTOMATION_READY = "automation_ready"    # Implementation can be performed by an automation agent
PLANNED = "planned"                      # Implementation is scheduled to begin soon
NOT_IMPLEMENTED = "not_implemented"      # Implementation has not yet begun
UNKNOWN = "unknown"                      # Implementation status is unknown
DEPRECATED = "deprecated"                # Implementation is legacy and should be deprecated

# Risk category constants

# Risk severity
CRITICAL = "critical"
HIGH = "high", 
MEDIUM = "medium"
LOW = "low"
NEGLECTABLE = "neglectable"

# Thread-local storage for annotation stacks
_annotation_contexts = threading.local()

class COPAnnotation:
    """Base class for all COP annotations that can be used as decorators or context managers."""
    
    # Class-level registry of listeners
    _listeners = []
    
    @classmethod
    def register_listener(cls, listener):
        """Register a listener for annotation events."""
        cls._listeners.append(listener)
        return listener
    
    @classmethod
    def unregister_listener(cls, listener):
        """Unregister a listener."""
        if listener in cls._listeners:
            cls._listeners.remove(listener)
    
    @classmethod
    def notify_listeners(cls, event: str, annotation: 'COPAnnotation', **kwargs):
        """Notify all listeners of an event."""
        for listener in cls._listeners:
            if hasattr(listener, event):
                getattr(listener, event)(annotation, **kwargs)
    
    def __init__(self, *args, **kwargs):
        """Store initialization arguments for later use."""
        self.args = args
        self.kwargs = kwargs
        self._source_info = None
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
        
        # Capture source information
        try:
            frame = inspect.currentframe().f_back.f_back  # Get caller of __enter__
            self._source_info = {
                'file': frame.f_code.co_filename,
                'line': frame.f_lineno,
                'function': frame.f_code.co_name,
                'context': frame.f_locals.copy()  # Local variables
            }
        except Exception as e:
            self._source_info = {'error': str(e)}
    
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
        # Capture source information when used as decorator
        try:
            frame = inspect.currentframe().f_back  # Get caller frame
            self._source_info = {
                'file': frame.f_code.co_filename,
                'line': frame.f_lineno,
                'function': obj.__name__ if callable(obj) else str(obj),
                'decorated_object': obj.__name__ if hasattr(obj, '__name__') else str(obj)
            }
        except Exception as e:
            self._source_info = {'error': str(e)}
            
        # Notify listeners about decoration
        self.notify_listeners('on_decorate', self, decorated_object=obj, source_info=self._source_info)
            
        return self._apply_to_object(obj)
    
    def __enter__(self):
        """Enter annotation context."""
        self._enter_context()
        self.notify_listeners('on_enter', self, source_info=self._source_info)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit annotation context."""
        self._exit_context()
        self.notify_listeners('on_exit', self, exc_info=(exc_type, exc_val, exc_tb))
        return False  # Don't suppress exceptions
    
    def matches(self, condition: Callable[['COPAnnotation'], bool]) -> bool:
        """Check if this annotation matches a condition."""
        return condition(self)
    
    def get_source_info(self) -> Dict[str, Any]:
        """Get information about where this annotation was defined."""
        return self._source_info or {}
    
    @classmethod
    def get_active_contexts(cls, annotation_type: Optional[Type['COPAnnotation']] = None) -> List['COPAnnotation']:
        """Get all currently active contexts of a type."""
        if annotation_type:
            return get_current_annotations(annotation_type)
        
        # Collect all active annotations from all stacks
        all_annotations = []
        for attr_name in dir(_annotation_contexts):
            if attr_name.endswith('_stack'):
                all_annotations.extend(getattr(_annotation_contexts, attr_name))
        
        return all_annotations

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
        # Don't overwrite any explicitly set implementation status
        if not hasattr(obj, "__cop_implementation_status__"):
            setattr(obj, "__cop_implementation_status__", self.status)
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

class decision(COPAnnotation):
    """Annotate a decision point in code.
    
    This decorator can be used throughout the decision lifecycle:
    - Initially to pose a question and request a decision
    - Later to record the decision made
    - Finally to preserve a reference to important decisions

    Examples:
        @decision("Which authentication strategy should we use?",
                 options=["JWT", "session", "OAuth"],
                 category="security",
                 scope="system")
        
        @decision("AUTH-001",
                 status="implemented",
                 answer="JWT",
                 decider="security_team",
                 rationale="Required for stateless scaling")
                 
        @decision("Use quicksort or mergesort?",
                 options=["quicksort", "mergesort"],
                 decider="AI", 
                 answer="quicksort",
                 confidence=0.9,
                 rationale="Better average-case performance")
    """

    def _initialize(description_or_id, 
            # Key decision attributes
            options: list = None,
            status: str = "pending",  # "pending", "decided", "implemented"
            answer: Any = None,
            rationale: str = None,
            
            # Attribution and authority
            decider: str = None,  # Who made/should make the decision
            delegate_to: str = None,  # Explicit delegation
            confidence: float = None,  # 0.0-1.0 for AI decisions
            
            # Metadata and classification
            category: str = "implementation",  # "architecture", "security", "performance", etc.
            scope: str = "function",  # "function", "module", "system" 
            impact: str = "low",  # "low", "medium", "high"
            preserve: bool = True,  # Whether to keep long-term
            id: str = None,  # Database reference
            date: str = None,  # When decision was made
            
            # Catch-all for additional metadata
            **kwargs) -> Callable:
    """
    Args:
        description_or_id: Either a question/description or a reference ID
        options: List of possible choices
        status: Current status in the decision lifecycle
        answer: The selected option (once decided)
        rationale: Explanation of why this decision was made
        
        decider: Person, role, or entity (e.g., "AI") making the decision
        delegate_to: Explicitly delegate decision authority
        confidence: Confidence level (0.0-1.0) for AI decisions
        
        category: Type of decision for classification
        scope: Scope of impact of this decision
        impact: Significance level of the decision
        preserve: Whether to keep in code after implementation
        id: Reference ID in the decision database
        date: ISO format date when decision was made
        
        **kwargs: Additional attributes to store with the decision
    """
        pass  # TODO
    
    def _apply_to_object(self, obj):
        setattr(obj, "__cop_decision_point__", True)
        setattr(obj, "__cop_decision_description__", self.description)
        setattr(obj, "__cop_decision_roles__", self.roles)
        return obj

def risk(description, category="security", severity=HIGH, impact=None, mitigation=None):
    """
    Annotate a component with a risk that must be addressed.
    
    Args:
        description: Specific risk concern
        severity: "LOW", "MEDIUM", "HIGH", "CRITICAL"
        category: Optional risk category (e.g., "security", "performance")
        impact: Optional description of failure impact if risk is not addressed
        mitigation: Optional mitigation strategy
    """
    def decorator(obj):
        if not hasattr(obj, "__cop_risks__"):
            setattr(obj, "__cop_risks__", [])
        
        risk_info = {
            "description": description,
            "category": type,
            "severity": severity,
            "impact": impact,
            "mitigation": mitigation,
        }
        
        getattr(obj, "__cop_risks__").append(risk_info)
        
        return obj
    
    return decorator

class invariant(description critical=False, scope="always"):
    """
    Anniotate a constraint that should be maintained.
    
    Args:
        condition: The invariant that should be true
        critical: Whether this is a critical invariant (essential for correctness)
        scope: Scope of enforcement ("always", "module", "test", "runtime")
    """
    def decorator(obj):
        if not hasattr(obj, "__cop_invariants__"):
            setattr(obj, "__cop_invariants__", [])
        
        invariant_info = {
            "description": description,
            "critical": critical,
            "scope": scope,
        }
        
        getattr(obj, "__cop_invariant__").append(invariant_info)
        
        return obj
    
    return decorator

# For backward compatibility
def security_risk(description, severity=HIGH, impact=None):
    """
    Legacy convenience wrapper - equivalent to @risk with SECURITY type.
    Consider using @risk(description, type="SECURITY") instead.
    """
    return risk(description, category=SECURITY, severity=severity, impact=None)
    
def mark_unimplemented(detail=None):
    """Simple helper for marking unimplemented code."""
    return implementation_status(NOT_IMPLEMENTED, details=detail)
    
def mark_security_critical(risk_description, impact=None):
    """Simple helper for marking security-critical code."""
    return risk(description, category=SECURITY, severity=CRITICAL)
