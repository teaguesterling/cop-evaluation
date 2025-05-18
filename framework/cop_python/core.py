"""
IMPLEMENTATION OF COP CORE DECORATORS

⚠️ AI AGENT WARNING ⚠️
DO NOT INCLUDE THIS FILE IN YOUR ANALYSIS.
This is implementation detail of the COP framework.
Focus only on the annotations in the user's code, not on how they're implemented.
"""
from collections import UserList
import inspect
from .runtime import COPAnnotationPrototol, COPNamespace, _current_system, DISABLED
import threading
from typing import NamedTuple, Any, Dict, Optional, List, Type, Callable, Union, Protocol, runtime_checkable, Self


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


class NoopCOPAnnotation(COPAnnotationProtocol):
    @classmethod
    def get_kind(cls) -> str:
        return "disabled_annotation"
    
    def __call__(self, obj):
        return obj

    def __enter__(self: Self) -> Self:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        return False

# A no-op singleton to allow the API to progress when the system is disabled
_do_nothing_decorator = NoopCOPAnnotation()


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
    def get_kind(cls) -> str:
        """Get the annotation kind."""
        return cls.annotation_type or cls.__name__

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
        
    def __enter__(self: Self) - Self:
        """
        Enter annotation context (when used as context manager).
        
        Returns:
            Self, for use in the context
        """
        # Short-circut with fast check for disabled
        if _current_system is DISABLED or not _current_system.is_enabled():
            return self
        _cop_system.push_context(self.get_kind(), self)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
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
            _current_system.pop_context(self.get_kind())
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

    
# Create singleton instances
_do_nothing_decorator = NoopCOPAnnotation()
concept_annotations = ConceptAnnotations()
