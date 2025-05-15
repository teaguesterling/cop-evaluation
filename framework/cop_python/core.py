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
BUGGY = "buggy"                          # Implementation is or was complete but has known bugs or failing tests
PARTIAL = "partial"                      # Implementation is incomplete but has begun
PLANNED = "planned"                      # Implementation is scheduled to begin soon
NOT_IMPLEMENTED = "not_implemented"      # Implementation has not yet begun
UNKNOWN = "unknown"                      # Implementation status is unknown
DEPRECATED = "deprecated"                # Implementation is legacy and should be deprecated

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
    """
    Annotate a decision point or implementation guidance in code.
    
    This versatile decorator can be used throughout the decision lifecycle:
    - Request a decision with options
    - Record a decision that was made
    - Document implementation guidance
    - Preserve architectural rationales
    
    Multiple decisions can be attached to a single component.
    
    Concise syntax for implementation guidance:
    @decision(implementor="ai")  # AI can implement (replaces AUTOMATION_READY)
    @decision(implementor="human")  # Human must implement (replaces REQUIRES_JUDGMENT)
    
    Examples of different decision types:
    
    # Security decision in progress
    @decision(
        "How should we store user passwords?",
        options=["bcrypt", "Argon2", "PBKDF2"],
        category="security",
        impact="high"
    )
    
    # Architectural decision already made
    @decision(
        "Should we use microservices?",
        status="implemented",
        answer="yes",
        decider="architecture_team",
        rationale="Enables independent scaling of components",
        reference_id="ARCH-042"
    )
    
    # Implementation guidance for AI
    @decision(
        implementor="ai",
        constraints=["Use parameterized queries", "Handle Unicode input"],
        reason="Standard validation function"
    )
    """
    
    def _initialize(self, description_or_id=None, 
                   # Implementation guidance (concise syntax)
                   implementor=None, constraints=None, reason=None,
                   
                   # Key decision attributes
                   options=None, status="pending", answer=None, rationale=None,
                   
                   # Attribution and authority
                   decider=None, delegate_to=None, confidence=None, 
                   
                   # Metadata and classification
                   category=None, scope="function", impact="low", priority="medium",
                   preserve=False, reference_id=None, date=None, **kwargs):
        self.description = description_or_id
        self.implementor = implementor
        self.constraints = constraints
        self.reason = reason
        self.options = options
        self.status = status
        self.answer = answer
        self.rationale = rationale
        self.decider = decider
        self.delegate_to = delegate_to
        self.confidence = confidence
        self.category = category
        self.scope = scope
        self.impact = impact
        self.priority = priority
        self.reference_id = reference_id
        self.date = date
        self.kwargs = kwargs
        self.preserve = preserve            
    
    def _apply_to_object(self, obj):
        # Create decision dictionary with all information
        decision_dict = {}
        
        # Add core decision information
        if self.description:
            decision_dict["description"] = self.description
        # Implementation guidance
        if self.implementor:
            decision_dict["implementor"] = self.implementor
            if self.constraints:
                decision_dict["constraints"] = self.constraints
            if self.reason:
                decision_dict["reason"] = self.reason
        # Decision details
        decision_dict["status"] = self.status
        if self.answer:
            decision_dict["answer"] = self.answer
        if self.rationale:
            decision_dict["rationale"] = self.rationale
        if self.decider:
            decision_dict["decider"] = self.decider
        if self.options:
            decision_dict["options"] = self.options
        # Metadata
        if self.reference_id:
            decision_dict["reference_id"] = self.reference_id
        if self.category:
            decision_dict["category"] = self.category
        if self.impact:
            decision_dict["impact"] = self.impact
        if self.scope != "function":
            decision_dict["scope"] = self.scope
        if self.priority != "medium":
            decision_dict["priority"] = self.priority
        decision_dict["preserve"] = self.preserve
        if self.date:
            decision_dict["date"] = self.date
        # Add any additional attributes
        for key, value in self.kwargs.items():
            decision_dict[key] = value
        # Initialize decisions list if it doesn't exist
        if not hasattr(obj, "__cop_decisions__"):
            setattr(obj, "__cop_decisions__", [])
            
        # Append this decision to the list
        getattr(obj, "__cop_decisions__").append(decision_dict)
            
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
