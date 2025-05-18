"""
IMPLEMENTATION OF COP CORE DECORATORS

⚠️ AI AGENT WARNING ⚠️
DO NOT INCLUDE THIS FILE IN YOUR ANALYSIS.
This is implementation detail of the COP framework.
Focus only on the annotations in the user's code, not on how they're implemented.
"""
import inspect
import threading
from collections import UserList
import datetime
from enum import Enum
from typing import NamedTuple, Any, Dict, Optional, List, Type, Callable, Union, Protocol, ClassVar
from .runtime import _current_system, DISABLED, resolve_concept


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


class COPAnnotationProtocol(Protocol):
    @classmethod
    def get_kind(self) -> str: ...
    def __call__(self, obj: Any) -> Any: ...
    def __enter_(self): ...
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool: ...


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
        return self.__getattr__(key)

    def __setitem__(self, key, value):
        """Prevent dictionary-style assignment."""
        raise TypeError(
            f"Dictionary-style assignment not supported for COPNamespace. "
            f"Use attribute style instead: annotations.{key} = {value!r}"
        )
    
    def __contains__(self, key):
        """Check if an annotation type exists."""
        return hasattr(self, key) and (not key.startswith('_')

    def get(self, key):
        return self.__getattr__(key)
    
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


class NoopCOPAnnotation(COPAnnotationProtocol):
    @classmethod
    def get_kind(cls):
        return "disabled_annotation"
    
    def __call__(self, obj):
        return obj

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, exc_tb):
        return False


class COPAnnotation(COPAnnotationData, COPAnnotationProtocol):
    """Base class for all COP annotations."""

    # To be adjusted in base classes if needed
    annotation_type: ClassVar[str] = None

    def __new__(cls, value=None, **kwargs):
        """Create a new annotation instance."""
        # Check for disabled mode
        if _current_system is DISABLED or not _current_system.is_enabled():
            return _do_nothing_decorator
        
        source_info = _current_system.get_source_info(skip_frames=2)
        instance = super().__new__(cls, value, kwargs, source_info)
        _current_system.notify_annotation_created(instance)
        return instance

    @classmethod
    def _make_metadata(cls, value, kwargs):
        return kwargs

    @classmethod
    def get_kind(cls):
        return self.annotation_type or self.__class__.__name__

    @classmethod
    def on(cls, concept, *args, **kwargs):
        """
        Apply an annotation to a concept externally.
        
        This method allows applying annotations to concepts from
        outside their definition, enabling externalized annotation.
        
        Args:
            concept: The concept to annotate
            *args, **kwargs: Arguments for the annotation
            
        Returns:
            The concept with the applied annotation
        """
        # Create the annotation
        annotation = cls(*args, **kwargs)
        resolved_concept = resolve_concept(concept)
        annotated_concept = annotation(resolved_concept)
        return annotated_concept

    @classmethod
    def create(cls, value, **kwargs):
        if _current_system is DISABLED or not _current_system.is_enabled():
            return _do_nothing_decorator
        else:
            return cls(value, **kwargs)

    @property
    def kind(self):
        return self.get_kind()

    def _apply_to_object(self, obj):
        """Apply this annotation to an object."""
        # Ensure annotations namespace exists
        if not hasattr(obj, "__cop_annotations__"):
            setattr(obj, "__cop_annotations__", COPNamespace())
        annotations = getattr(obj, "__cop_annotations__")
        annotations.get(self.kind).append(self)
        return obj
    
    def __call__(self, obj=None):
        """Apply annotation to an object."""
        # Quick return if disabled
        if _current_system is DISABLED or not _current_system.is_enabled():
            return obj if obj is not None else self
        
        if obj is not None:
            # Apply to the provided object
            return self._apply_to_object(obj)
        
        # No object provided, return self
        return self
        
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
        

class COPSingletonAnnotation(COPAnnotation):
    def _apply_to_object(self, obj):
        annotations = getattr(obj, "__cop_annotations__").get(self.kind)
        if len(annotations) > 0:
            raise DuplicateAnnotationError(f"No more than one {self.kind} COP annotation can be added to {obj.__name__}")
        super()._register_annotation(obj)


class COPAnnotations(UserList):
    """A collection of annotations."""
    
    def __init__(self, annotations=None, on=None):
        super().__init__(annotations or [])
        self._explicit_scope = on
        self._detected_scope = None
    
    def __enter__(self):
        # Determine scope (explicit or automatic)
        if self._explicit_scope is None:
            system = get_system()
            self._detected_scope = system.determine_scope(inspect.currentframe().f_back)
        
        # Register as handler
        system = get_system()
        system.push_context("annotation_handler", self)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Unregister
        get_system().pop_context("annotation_handler")
        self._detected_scope = None
        return False
    
    def handle_annotation(self, annotation):
        """Handle a newly created annotation."""
        # Store the annotation (using UserList's append)
        self.append(annotation)
        
        # Apply to appropriate scope
        scope = self._explicit_scope or self._detected_scope
        if scope:
            annotation(scope)
    
    def apply_to(self, obj):
        """Apply all annotations in this set to an object."""
        for annotation in self:
            annotation(obj)
        return obj
    
    # Additional "set-like" methods that might be useful
    def union(self, other):
        """Create a new set with annotations from both sets."""
        return self.__class__(self + list(other), on=self._explicit_scope)
    
    def filter(self, kind=None, **kwargs):
        """Filter annotations by type and/or properties."""
        kind = kind if isinstance(kind, str) else kind.get_kind()
        missing = object()
        result = []
        for anno in self:
            if kind and anno.kind != kind:
                continue
            for key, value in kwargs.items():
                if getattr(anno, key, missing) is missing:
                    break
            else:
                result.append(anno)
        return self.__class__(result, on=self._explicit_scope)
    
    def get_scope(self):
        """Get the current scope being annotated."""
        return self._explicit_scope or self._detected_scope
    
    @classmethod
    def from_annotations(cls, *annotations, on=None):
        """Create a set from existing annotations."""
        return cls(annotations=annotations, on=on)


class Intent(COPSingletonAnnotation):
    """
    Document the intended purpose of a concept.
    
    This decorator captures what a concept is supposed to do,
    separate from its actual implementation.
    
    Examples:
        @intent("Process user payments securely")
        def process_payment(payment_data):
            # Implementation
            
        # As a context manager (for specific code sections)
        with intent("Calculate tax based on jurisdiction"):
            tax = calculate_tax(amount, location)
    """
    annotation_type = "intent"

    @classmethod
    def create(cls, description: str): 
        """
        Initialize intent annotation.
        
        Args:
            description: Description of the intent
        """
        return super().create(description)
 

class ImplementationStatus(COPSingletonAnnotation):
    """
    Explicitly mark concept implementation status.
    
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
    annotation_type = "implementation_status"

    @classmethod
    def create(cls, status, *, details: Optional[str]=None, alternative: Optional[str]=None):
        """
        Initialize implementation status annotation.
        
        Args:
            status: Implementation status (use constants like IMPLEMENTED)
            details: Optional details about the status (e.g., limitations)
            alternative: For DEPRECATED status, what to use instead
        """
        metadata = {}
        if details is not None:
            metadata["details"] = details
        if alternative is not None:
            metadata["alternative"] = alternative
        return super().create(status, **metadata)


class Invariant(COPAnnotation):
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
    annotation_type = "invariant"
    
    def create(self, condition: str, *, critical: bool=False, scope: str="always"):
        """
        Initialize invariant annotation.
        
        Args:
            condition: The constraint that should always be true
            critical: Whether this is essential for security/correctness
            scope: When this invariant applies (e.g., "always", "runtime")
        """
        return super().create(condition, critical=critical, scope=scope)


class Risk(COPAnnotation):
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
    annotation_type = "risk"
    
    def create(self, description: str, *, category: str="security", severity: str="MEDIUM", 
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
        metadata = {
            "category": category,
            "severity": severity,
        }
        if impact is not None:
            metadata["impact"] = impact
        if mitigation is not None:
            metadata["mitigation"] = mitigation
        return super().create(description, **metadata)


class Decision(COPAnnotation):
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
    annotation_type = "decision"

    @classmethod
    def create(cls, 
               # Short and optional longer decision description
               brief="implementation boundary", *, description=None,
               # Implementation guidance (concise syntax)
               implementor=None, constraints=None, reason=None,
               # Key decision attributes
               options=None, status=None, answer=None, rationale=None,
               # Attribution and authority
               decider=None, delegate=None, confidence=None, 
               # Metadata and classification
               category=None, scope=None, impact=None, priority=None,
               preserve=None, ref=None, date=None, see_also=None, 
               **kwargs):
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
        metadata = {}
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
        metadata.update(kwargs)
        return super().create(brief, **metadata)

    
# Create singleton instances
_do_nothing_decorator = NoopCOPAnnotation()
concept_annotations = ConceptAnnotationSet()

# Expose create methods for annotations
intent = Intent.create
implementation_status = ImplementationStatus.create
invariant = Invariant.create
risk = Risk.create
decision = Decision.create

# Expose the ImplementationStatusValues as module-level constants
IMPLEMENTED = ImplementationStatusValues.IMPLEMENTED         # ✅ Fully functional and complete
PARTIAL = ImplementationStatusValues.PARTIAL                 # ⚠️ Partially working with limitations
BUGGY = ImplementationStatusValues.BUGGY                     # ❌ Was working but now has issues
DEPRECATED = ImplementationStatusValues.DEPRECATED           # 🚫 Exists but should not be used
PLANNED = ImplementationStatusValues.PLANNED                 # 📝 Designed but not implemented
NOT_IMPLEMENTED = ImplementationStatusValues.NOT_IMPLEMENTED # ❓ Does not exist at all
UNKNOWN = ImplementationStatusValues.UNKNOWN                 # ❔ Status not yet evaluated
