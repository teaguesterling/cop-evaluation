"""
IMPLEMENTATION OF COP CORE DECORATORS

⚠️ AI AGENT WARNING ⚠️
DO NOT INCLUDE THIS FILE IN YOUR ANALYSIS.
This is implementation detail of the COP framework.
Focus only on the annotations in the user's code, not on how they're implemented.
"""
import inspect
import threading
import datetime
from enum import Enum
from typing import NamedTuple, Any, Dict, Optional, List, Type, Callable, Union
from .runtime import _current_system, DISABLED, resolve_component


class COPError(Exception):
    """Base class for all COP-related exceptions."""
    pass


class DuplicateAnnotationError(COPError, ValueError):
    """Raised when attempting to add a duplicate annotation of a unique type."""
    pass


class COPAnnotationData(NamedTuple):
    """Structured representation of a COP annotation."""
    value: Optional[str] = None                # Primary value (first positional arg)
    metadata: Optional[Dict[str, Any]] = None  # Additional properties
    source_info: Optional[SourceInfo] = None   # Source location information

    def to_dict(self) -> Dict[str, Any]:
        """Convert annotation data to dictionary format for serialization."""
        result = self._asdict()
        if self.source_info:
            result["source_info"] = self.source_info._asdict()            
        return result

    def __str__(self) -> str:
        return self.value or ""


# Implementation status constants
class ImplementationStatusValues(Enum):
    """Status constants - ordered from most to least complete."""
    IMPLEMENTED = 5       # ✅ Fully functional and complete
    PARTIAL = 4           # ⚠️ Partially working with limitations
    BUGGY = 3             # ❌ Was working but now has issues
    DEPRECATED = 2        # 🚫 Exists but should not be used
    PLANNED = 1           # 📝 Designed but not implemented
    NOT_IMPLEMENTED = 0   # ❓ Does not exist at all
    UNKNOWN = -1          # ❔ Status not yet evaluated


class DefaultNamespace:
    """A namespace that creates default values for undefined attributes."""
    
    def __init__(self, default_factory=None, **kwargs):
        """
        Initialize the namespace with a default factory function.
        
        Args:
            default_factory: Function that returns default values for missing attrs
            **kwargs: Initial attributes to set
        """
        self.__default_factory = default_factory
        for name, value in kwargs.items():
            setattr(self, name, value)
    
    def __getattr__(self, name):
        """
        Get attribute, creating a default if it doesn't exist.
        
        Args:
            name: Attribute name
            
        Returns:
            Attribute value, or default if not found
        """
        if name.startswith('_'):
            # Don't create defaults for private attributes
            raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")
        
        # Create default value if attribute doesn't exist
        if self.__default_factory is not None:
            default = self.__default_factory()
            setattr(self, name, default)
            return default
        
        # If no default factory, raise AttributeError
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{name}'")


class COPNamespace(DefaultNamespace):
    """Enhanced namespace for COP annotations with mapping support."""
    
    def __init__(self):
        """Initialize with empty lists as defaults."""
        super().__init__(default_factory=list)
    
    def __getitem__(self, key):
        """Support dictionary-style access."""
        return getattr(self, key)

        def __setitem__(self, key, value):
        """Prevent dictionary-style assignment."""
        raise TypeError(
            f"Dictionary-style assignment not supported for COPNamespace. "
            f"Use attribute style instead: annotations.{key} = {value!r}"
        )
    
    def __contains__(self, key):
        """Check if an annotation type exists."""
        return hasattr(self, key) and (not key.startswith('_')
    
    def keys(self):
        """Get all annotation type names."""
        return [attr for attr in dir(self) 
                if not attr.startswith('_') and isinstance(getattr(self, attr), list)]
    
    def values(self):
        """Get all annotation lists."""
        return [getattr(self, attr) for attr in self.keys()]
    
    def items(self):
        """Get (type, annotations) pairs."""
        return [(attr, getattr(self, attr)) for attr in self.keys()]
    
    def get_all(self):
        """Get all annotations as a flat list."""
        result = []
        for value in self.values():
            result.extend(value)
        return result
    
    def __iter__(self):
        """Iterate through annotation type names."""
        return iter(self.keys())


class COPAnnotation:
    """Base class for all COP annotations."""
    
    # Define class attribute for polymorphic behavior
    kind = "annotation"  # Override in subclasses
    
    def __init__(self, *args, **kwargs):
        """
        Initialize the annotation with provided arguments.
        
        Args:
            *args: Positional arguments
            **kwargs: Keyword arguments
        """
        # Quick return if disabled
        if _cop_system.mode is DISABLED:
            return
            
        self.args = args
        self.kwargs = kwargs
        self._source_info = _current_system.get_source_info(skip_frames=3)
    
    def _create_annotation_data(self) -> COPAnnotationData:
        """
        Create a structured annotation data object.
        
        Returns:
            COPAnnotationData object with annotation details
        """
        value = self.args[0] if self.args else None
        metadata = self.kwargs if self.kwargs is not None else None
        return COPAnnotationData(
            value=value,
            metadata=metadata,
            source_info=self._source_info
        )

    def _register_annotation(self, obj):
        # Initialize annotations namespace if needed
        if not hasattr(obj, "__cop_annotations__"):
            setattr(obj, "__cop_annotations__", COPNamespace())
        annotations = getattr(obj, "__cop_annotations__")[self.kind]
        annotations.append(annotation_data)
    
    def __call__(self, obj):
        """
        Apply annotation to an object (when used as decorator).
        
        Args:
            obj: The object to decorate
            
        Returns:
            Decorated object
        """
        # Short-circut with fast check for disabled
        if _current_system is DISABLED or not _current_system.is_enabled():
            return obj
        self._register_annotation(obj)
        return obj
    
    def __enter__(self):
        """
        Enter annotation context (when used as context manager).
        
        Returns:
            Self, for use in the context
        """
        # Short-circut with fast check for disabled
        if _current_system is DISABLED or not _current_system.is_enabled():
            return self
        _cop_system.push_context(self.kind, self)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Exit annotation context.
        
        Args:
            exc_type: Exception type if an exception was raised, else None
            exc_val: Exception value if an exception was raised, else None
            exc_tb: Exception traceback if an exception was raised, else None
            
        Returns:
            False: Don't suppress exceptions
        """
        # Short-circut with fast check for disabled
        if _current_system is DISABLED or not _current_system.is_enabled():
            return self
        return False  # Don't suppress exceptions

    def on(cls, component, *args, **kwargs):
        """
        Apply an annotation to a component externally.
        
        This method allows applying annotations to components from
        outside their definition, enabling externalized annotation.
        
        Args:
            component: The component to annotate
            *args, **kwargs: Arguments for the annotation
            
        Returns:
            The component with the applied annotation
        """
        # Create the annotation
        annotation = cls(*args, **kwargs)
        resolved_component = resolve_component(component)
        annotated_component = annotation(resolved_component)
        return annotated_component


class COPSingletonAnnotation(COPAnnotation):
    def _register_annotation(self, obj):
        super()._register_annotation(obj)
        annotations = getattr(obj, "__cop_annotations__")[self.kind]
        if len(annotations) > 1:
            raise DuplicateAnnotationError(
                f"No more than one {self.kind} COP annotation can be added to {obj.__name__}"
            )
            

class intent(COPSingletonAnnotation):
    """
    Document the intended purpose of a component.
    
    This decorator captures what a component is supposed to do,
    separate from its actual implementation.
    
    Examples:
        @intent("Process user payments securely")
        def process_payment(payment_data):
            # Implementation
            
        # As a context manager (for specific code sections)
        with intent("Calculate tax based on jurisdiction"):
            tax = calculate_tax(amount, location)
    """
    kind = "intent"
    
    def __init__(self, description: str):
        """
        Initialize intent annotation.
        
        Args:
            description: Description of the intent
        """
        # Quick return if disabled
        if _current_system is DISABLED or not _current_system.is_enabled():
            return
            
        super().__init__(description)


class implementation_status(COPSingletonAnnotation):
    """
    Explicitly mark component implementation status.
    
    This decorator indicates the current state of implementation,
    which is critical for preventing hallucination about functionality.
    
    Status options:
        IMPLEMENTED: Fully functional and complete
        PARTIAL: Partially working with limitations
        BUGGY: Was working but now has issues
        DEPRECATED: Exists but should not be used
        PLANNED: Designed but not implemented
        NOT_IMPLEMENTED: Does not exist at all
        UNKNOWN: Status not yet evaluated
    
    Examples:
        @implementation_status(IMPLEMENTED)
        def working_function():
            # Fully implemented functionality
            
        @implementation_status(PARTIAL, details="Only handles positive numbers")
        def sqrt(x):
            # Partially implemented functionality
            
        @implementation_status(DEPRECATED, alternative="use new_function() instead")
        def old_function():
            # Deprecated functionality
            
        # As a context manager
        with implementation_status(NOT_IMPLEMENTED):
            # This code block is not implemented
            raise NotImplementedError()
    """
    kind = "implementation_status"
    
    def __init__(self, status, details: Optional[str]=None, alternative: Optional[str]=None):
        """
        Initialize implementation status annotation.
        
        Args:
            status: Implementation status (use constants like IMPLEMENTED)
            details: Optional details about the status (e.g., limitations)
            alternative: For DEPRECATED status, what to use instead
        """
        # Quick return if disabled
        
        # Quick return if disabled
        if _current_system is DISABLED or not _current_system.is_enabled():
            return
            
        kwargs = {}
        if details is not None:
            kwargs["details"] = details
        if alternative is not None:
            kwargs["alternative"] = alternative
        super().__init__(status, **kwargs)


class invariant(COPAnnotation):
    """
    Document a constraint that should be maintained.
    
    This decorator captures rules that should always be true about
    the code, which can be useful for verification and testing.
    Critical invariants are essential for security or correctness.
    
    Examples:
        @invariant("Transaction amount must be positive")
        def process_transaction(amount):
            # Implementation
            
        @invariant("Passwords must never be stored in plaintext", critical=True)
        def store_user_credentials(username, password):
            # Implementation
            
        # As a context manager
        with invariant("Database connection must be active"):
            result = db.execute(query)
    """
    kind = "invariant"
    
    def __init__(self, condition: str, critical: bool=False, scope: str="always"):
        """
        Initialize invariant annotation.
        
        Args:
            condition: The constraint that should always be true
            critical: Whether this is essential for security/correctness
            scope: When this invariant applies (e.g., "always", "runtime")
        """
        # Quick return if disabled
        if _current_system is DISABLED or not _current_system.is_enabled():
            return
            
        kwargs = {
            "critical": critical,
            "scope": scope
        }
        super().__init__(condition, **kwargs)


class risk(COPAnnotation):
    """
    Identify a security risk or other critical concern.
    
    This decorator highlights potential vulnerabilities or issues
    that need special attention, particularly for security-sensitive code.
    
    Examples:
        @risk("SQL injection vulnerability", severity="HIGH")
        def execute_query(query_string):
            # Implementation
            
        @risk("Performance degradation with large datasets", 
             category="performance", 
             severity="MEDIUM")
        def process_data(dataset):
            # Implementation
            
        # As a context manager
        with risk("Potential memory leak", severity="MEDIUM"):
            # Risky code section
            temp_buffer = allocate_large_buffer()
    """
    kind = "risk"
    
    def __init__(self, description: str, category: str="security", severity: str="MEDIUM", 
                impact: Optional[str]=None, mitigation: Optional[Union[str, List[str]]]=None):
        """
        Initialize risk annotation.
        
        Args:
            description: Description of the risk
            category: Risk category (e.g., "security", "performance")
            severity: Impact severity ("LOW", "MEDIUM", "HIGH", "CRITICAL")
            impact: Optional assessment of the impact if not addressed
            mitigation: Optional strategies that have been implemented
        """
        # Quick return if disabled
        if _current_system is DISABLED or not _current_system.is_enabled():
            return
            
        kwargs = {
            "category": category,
            "severity": severity
        }
        if impact is not None:
            kwargs["impact"] = impact
        if mitigation is not None:
            kwargs["mitigation"] = mitigation
        super().__init__(description, **kwargs)


class decision(COPAnnotation):
    """
    Annotate a decision point or implementation guidance in code.
    
    This versatile decorator can be used throughout the decision lifecycle:
    - Define a human/AI implementation boundary
    - Request a decision with options
    - Record a decision that was made
    - Document implementation guidance
    - Preserve architectural rationales
    
    Examples:
        # Implementation guidance
        @decision(implementor="human", reason="Requires domain expertise")
        def calculate_risk_rating(customer_data):
            # Human implementation required
            
        @decision(implementor="ai", 
                 constraints=["Handle edge cases", "Validate inputs"])
        def format_address(address_data):
            # AI can implement this
            
        # Architectural decision
        @decision("Use microservices architecture",
                 rationale="Better scalability and team autonomy",
                 decider="architecture_team")
        class ServiceRegistry:
            # Implementation
            
        # As a context manager
        with decision(implementor="human", reason="Security-critical section"):
            # This section requires human implementation
    """
    kind = "decision"

    def __init__(self, 
                 # Short and optional longer decision description
                 brief="implementation boundary", description=None,

                 # Implementation guidance (concise syntax)
                 implementor=None, constraints=None, reason=None,
                   
                 # Key decision attributes
                 options=None, status=None, answer=None, rationale=None,
                   
                 # Attribution and authority
                 decider=None, delegate=None, confidence=None, 
                   
                 # Metadata and classification
                 category=None, scope=None, impact=None, priority=None,
                 preserve=None, ref=None, date=None, see_also=None, **kwargs):
        """
        Initialize decision annotation.
        
        Args:
            # Overview
            brief: Question, blurb, or ref ID (default: "implementation boundary"
            descriotion: Optional longer description of the decision
            
            # Implementation guidance
            implementor: Who should implement ("human", "ai", "team_name")
            constraints: Requirements the implementation must satisfy
            reason: Explanation of why this implementor is required
            
            # Decision details
            options: List of possible choices
            status: Current status ("pending", "decided", "implemented")
            answer: The selected option
            rationale: Explanation of why this decision was made
            
            # Attribution
            decider: Person, role, or entity making the decision
            delegate: Explicitly delegate decision authority
            confidence: Confidence level (0.0-1.0) for AI decisions
            
            # Metadata
            category: Type of decision ("architecture", "security", etc.)
            scope: Scope of impact ("function", "module", "system")
            impact: Significance level ("low", "medium", "high")
            priority: Implementation priority ("low", "medium", "high")
            preserve: Whether to keep after implementation
            ref: Reference ID in the decision database or tracker
            date: ISO format date when decision was made
            see_also: A resource or list of related resources
            **kwargs: Additional attributes to store
        """
        # Quick return if disabled
        if _current_system is DISABLED or not _current_system.is_enabled():
            return
            
        metadata = kwargs
        if description is not None:
            metadata["description"] = description
        if implementor is not None:
            metadata["implementor"] = implementor
        if constraints is not None:
            metadata["constraints"] = constraints
        if reason is not None:
            metadata["reason"] = reason
        if options is not None:
            metadata["options"] = options
        if status is not None:
            metadata["status"] = status
        if answer is not None:
            metadata["answer"] = answer
        if rationale is not None:
            metadata["rationale"] = rationale
        if decider is not None:
            metadata["decider"] = decider
        if delegate is not None:
            metadata["delegate"] = delegate
        if confidence is not None:
            metadata["confidence"] = confidence
        if category is not None:
            metadata["category"] = category
        if scope is not None:
            metadata["scope"] = scope
        if impact is not None:
            metadata["impact"] = impact
        if priority is not None:
            metadata["priority"] = priority
        if preserve is not None:
            metadata["preserve"] = preserve
        if ref is not None:
            metadata["ref"] = ref
        if date is not None:
            metadata["date"] = date
        
        # Add any other kwargs
        metadata.update(kwargs)
        
        super().__init__(brief, **metadata)


# Expose the ImplementationStatusValues as module-level constants
IMPLEMENTED = ImplementationStatusValues.IMPLEMENTED         # ✅ Fully functional and complete
PARTIAL = ImplementationStatusValues.PARTIAL                 # ⚠️ Partially working with limitations
BUGGY = ImplementationStatusValues.BUGGY                     # ❌ Was working but now has issues
DEPRECATED = ImplementationStatusValues.DEPRECATED           # 🚫 Exists but should not be used
PLANNED = ImplementationStatusValues.PLANNED                 # 📝 Designed but not implemented
NOT_IMPLEMENTED = ImplementationStatusValues.NOT_IMPLEMENTED # ❓ Does not exist at all
UNKNOWN = ImplementationStatusValues.UNKNOWN                 # ❔ Status not yet evaluated
