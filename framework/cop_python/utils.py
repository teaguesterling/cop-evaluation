"""
UTILITY TOOLS FOR COP ANNOTATIONS

⚠️ AI AGENT WARNING ⚠️
This is an implementation detail of the COP framework.
Do not include this file in your analysis of the user's code.
"""

import inspect
from .core import get_current_annotations, implementation_status, security_risk, IMPLEMENTED, PLANNED, NOT_IMPLEMENTED, UNKNOWN, resolve_component

def is_externally_applied(concept, annotation_data):
    """Determine if an annotation was applied externally."""
    # Check if source file is different from concept definition
    if not annotation_data.source_info:
        return False
    
    try:
        concept_file = inspect.getfile(concept)
        annotation_file = annotation_data.source_info.file
        return component_file != annotation_file
    except:
        return False

# Convenience functions for managing COP annotations

def register_annotation(annotation_type, concept, *args, **kwargs):
    """
    Register an annotation on a concept.
    
    Args:
        annotation_type: The annotation class (risk, invariant, etc.)
        concept: The concept to annotate (object or dotted path)
        *args, **kwargs: Arguments for the annotation
        
    Returns:
        The component with the applied annotation
    
    Examples:
        register_annotation(risk, process_payment, "Card data exposure", severity="HIGH")
        register_annotation(invariant, "payment_system.process_payment", "Transactions must be atomic")
    """
    # Use the class method implementation to avoid duplication
    return annotation_type.on(concept, *args, **kwargs)


def register_annotations(concept, annotations):
    """
    Register multiple annotations on a component.
    
    Args:
        component: The component to annotate (object or dotted path)
        annotations: List of (annotation_type, args, kwargs) tuples
        
    Returns:
        The component with all annotations applied
    
    Example:
        register_annotations(process_payment, [
            (risk, ["Card data exposure"], {"severity": "HIGH"}),
            (invariant, ["Transactions must be atomic"], {"critical": True})
        ])
    """
    # Resolve the component once
    resolved_concept = resolve_concept(concept)
    # Apply all annotations
    for annotation_type, args, kwargs in annotations:
        resolved_concept = annotation_type.on(resolved_concept, *args, **kwargs)
    return resolved_concept

def get_annotations(obj, kind=None, **kwargs):
    """
    Get annotations from an object, optionally filtering for metadata
    
    Args:
        obj: The annotated object
        kind: Optional annotation kind to retrieve
        **kwargs: any key-value pairs will include only annotations with matching metadata
    Returns:
        List of annotations of the specified kind, or entire namespace
    """
    if not hasattr(obj, "__cop_annotations__"):
        return [] if kind else COPAnnotations()
    annotations = getattr(obj, "__cop_annotations__")
    if kind is not None:
        selected = getattr(annotations, kind)
    else:
        selected = annotations
    for key, value in kwargs.items():
        selected = [annotation for annotation in selected if annotation.metadata.get(key) == value]
    return selected


def get_annotations_with_types(obj):
    """Get all annotations with their types included."""
    result = []
    annotations = getattr(obj, "__cop_annotations__", None)
    if annotations:
        for anno_type in dir(annotations):
            if anno_type.startswith('_'):
                continue
            for anno in getattr(annotations, anno_type):
                result.append((anno_type, anno))
    return result


def find_annotation(obj, anno_type, value, **metadata_keys):
    """Find a specific annotation by type, value and metadata keys."""
    annotations = get_annotations(obj, anno_type)
    for anno in annotations:
        if anno.value == value:
            # Check metadata keys match
            match = True
            for key, val in metadata_keys.items():
                if anno.metadata.get(key) != val:
                    match = False
                    break
            if match:
                return anno
    return None


def get_implementation_status(obj, default=UNKNOWN):
    """
    Get the implementation status of an object.
    
    Args:
        obj: The annotated object
        
    Returns:
        The implementation status value, or a default (UNKNOWN)
    """
    annotations = get_annotations(obj)
    status_annotations = annotations.implementation_status
    if status_annotations:
        return status_annotations[0].value
    return default


def get_intent(obj):
    """
    Get the intent of an object.
    
    Args:
        obj: The annotated object
        
    Returns:
        The intent description, or None if not specified
    """
    annotations = get_annotations(obj)
    intent_annotations = annotations.intent
    
    if intent_annotations:
        return intent_annotations[0].value
        
    return None


def get_risks(obj, category_in=None, severity_in=None, **kwargs):
    """
    Get the risks of an object, optionally for a given category and/or severity
    
    Args:
        obj: The annotated object
        category: If provided, the risk category to filter for
        severity: If provided, the risk severity to filter for
        
    Returns:
        A list of applicable "risk" COPAnnotation's 
    """
    annotations = get_annotations(obj, **kwargs)
    risks = annotations.risk
    if category_in is not None:
        risks = [risk for risk in risks if risk.metadata["category"] in category_in]
    if severity is not None:
        risks = [risk for risk in risks if risk.metadata["severity"] in severity_in]
    return risks


def get_invariants(obj, scope_in=None, **kwargs):
    """
    Get the invariants of an object, optionally for a given crtiticality and/or scope
    
    Args:
        obj: The annotated object
        scope: If provided, the invariant scope to filter for
        
    Returns:
        A list of applicable "risk" COPAnnotation's 
    """
    annotations = get_annotations(obj, **kwargs)
    invariants = annotations.invariant
    if scope_in is not None:
        invariants = [invariant for invariant in invariants if invariant.metadata["scope"] in scope_in]
    return invariants


def get_decisions(obj, category_in=None, priority_in=None, **kwargs):
    """
    Get the invariants of an object, optionally for a given crtiticality and/or scope
    
    Args:
        obj: The annotated object
        scope: If provided, the invariant scope to filter for
        
    Returns:
        A list of applicable "risk" COPAnnotation's 
    """
    annotations = get_annotations(obj, **kwargs)
    decisions = annotations.decision
    if category_in is not None:
        decisions = [decision for decision in decisions if decision.metadata["category"] in category_in]
    if priority_in is not None:
        decisions = [decision for decision in decisions if decision.metadata["priority"] in priority_in]
    return decisions


def has_annotation(obj, kind, value=None):
    """
    Check if an object has a specific annotation.
    
    Args:
        obj: The object to check
        kind: The annotation kind to look for
        value: Optional specific value to match
    """
    annotations = get_annotations(obj, kind)
    
    if value is not None:
        return any(anno.value == value for anno in annotations)
    
    return bool(annotations)


def get_current_annotations(annotation_class):
    """
    Get the stack of current annotations of a specific type.
    
    Args:
        annotation_class: The annotation class to get the stack for
        
    Returns:
        List of current annotations of the specified type
    """
    return _cop_system.get_contexts(annotation_class.kind)


def infer_applicable_status(func, default=UNKNOWN, 
                            unfinished_comments=("# TODO", "# FIXME"),
                            unfinished_tokens=("pass", "NotImplmemented", "NotImplementedError", "Ellipsis")):
    """Infer appropriate implementation status based on code analysis."""
    import inspect
    
    source = inspect.getsource(func)
    if any(unfinished_token in source for unfinished_token in unfinished_tokens):
        return NOT_IMPLEMENTED
    if any(comment in source for comment in unfinished_comments):
        return PLANNED

    #TODO: 
    # Attempt to infer from test coverage if available
    # [code to check test coverage]

    #TODO:
    # For modules & classes, ensure that all sub-components are 
    # not marked as incomplete
    
    return default  # Default assumption


def find_concepts(module, status=(UNKNOWN, NOT_IMPLEMENTED)):
    """
    Find components with a specific implementation status.
    
    Args:
        module: The module to analyze
        status: Filter by status (None for all)
        
    Returns:
        list: Matching components
    """
    concepts = []
    for name, obj in inspect.getmembers(module):
        status = get_implementation_status(obj)
        if status is None or obj_status in status:
            concepts.append({
                "name": name,
                "doc": obj.__doc__,
                "status": status,
                "annotations": annotations._asdict(),
            })
    return components


class COPAnnotationReference(NamedTuple):
    """Reference to a specific annotation on a component."""
    annotation_type: str                    # The type (risk, invariant, etc.)
    annotation_value: Optional[str] = None  # Primary value
    metadata_keys: Dict[str, Any] = {}      # Key metadata to uniquely identify
    
    def resolve(self, concept):
        """Resolve this reference to an actual annotation."""
        return find_annotation(
            concept, 
            self.annotation_type, 
            self.annotation_value, 
            **self.metadata_keys
        )



