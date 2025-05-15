"""
UTILITY TOOLS FOR COP ANNOTATIONS

⚠️ AI AGENT WARNING ⚠️
This is an implementation detail of the COP framework.
Do not include this file in your analysis of the user's code.
"""

import inspect
from .core import get_current_annotations, implementation_status, security_risk, IMPLEMENTED, PLANNED, NOT_IMPLEMENTED

def get_applicable_status(func, default=IMPLEMENTED, unfinished_comments=["# TODO", "# FIXME"]):
    """Infer appropriate implementation status based on code analysis."""
    import inspect
    
    source = inspect.getsource(func)
    if "pass" in source or "NotImplementedError" in source:
        return NOT_IMPLEMENTED
    if any(comment in source for comment in unfinished_comments):
        return PLANNED

    #TODO: 
    # Attempt to infer from test coverage if available
    # [code to check test coverage]
    
    return default  # Default assumption

def get_cop_metadata(obj):
    """
    Extract all COP-related metadata from an object.
    
    Args:
        obj: The object to analyze
        
    Returns:
        dict: Metadata dictionary
    """
    metadata = {
        "intent": getattr(obj, "__cop_intent__", None),
        "implementation_status": getattr(obj, "__cop_implementation_status__", "implemented"),
        "invariants": getattr(obj, "__cop_invariants__", []),
        "critical_invariants": getattr(obj, "__cop_critical_invariants__", []),
        "security_risk": getattr(obj, "__cop_security_risk__", None),
        "security_severity": getattr(obj, "__cop_security_severity__", None)
    }
    
    # Add decision point info if present
    if getattr(obj, "__cop_decision_point__", False):
        metadata["decision_point"] = {
            "description": getattr(obj, "__cop_decision_description__", None),
            "roles": getattr(obj, "__cop_decision_roles__", None)
        }
    
    # Add constraints if AUTOMATION_READY
    if metadata["implementation_status"] == "automation_ready":
        metadata["constraints"] = getattr(obj, "__cop_constraints__", [])
    
    # Add alternative if DEPRECATED
    if metadata["implementation_status"] == "deprecated":
        metadata["alternative"] = getattr(obj, "__cop_alternative__", None)
    
    return metadata

def find_security_risks(module):
    """
    Find all security risks in a module.
    
    Args:
        module: The module to analyze
        
    Returns:
        list: Components with security risks
    """
    risks = []
    
    for name, obj in inspect.getmembers(module):
        if hasattr(obj, "__cop_security_risk__"):
            risks.append({
                "name": name,
                "risk": getattr(obj, "__cop_security_risk__"),
                "severity": getattr(obj, "__cop_security_severity__", "HIGH"),
                "implementation_status": getattr(obj, "__cop_implementation_status__", "implemented")
            })
            
        # Also check methods if it's a class
        if inspect.isclass(obj):
            for method_name, method in inspect.getmembers(obj, predicate=inspect.isfunction):
                if hasattr(method, "__cop_security_risk__"):
                    risks.append({
                        "name": f"{name}.{method_name}",
                        "risk": getattr(method, "__cop_security_risk__"),
                        "severity": getattr(method, "__cop_security_severity__", "HIGH"),
                        "implementation_status": getattr(method, "__cop_implementation_status__", "implemented")
                    })
    
    return risks

def find_components(module, status=None):
    """
    Find components with a specific implementation status.
    
    Args:
        module: The module to analyze
        status: Filter by status (None for all)
        
    Returns:
        list: Matching components
    """
    components = []
    
    for name, obj in inspect.getmembers(module):
        if hasattr(obj, "__cop_implementation_status__"):
            obj_status = getattr(obj, "__cop_implementation_status__")
            
            if status is None or obj_status == status:
                components.append({
                    "name": name,
                    "status": obj_status,
                    "intent": getattr(obj, "__cop_intent__", None)
                })
    
    return components

def get_current_context_metadata():
    """
    Get metadata about the current code context from context managers.
    
    Returns:
        dict: Current context metadata
    """
    context = {}
    
    # Check implementation status contexts
    impl_contexts = get_current_annotations(implementation_status)
    if impl_contexts:
        current = impl_contexts[-1]  # Get the innermost context
        context["implementation_status"] = current.status
        if current.details:
            context["implementation_details"] = current.details
    
    # Check security risk contexts
    security_contexts = get_current_annotations(security_risk)
    if security_contexts:
        current = security_contexts[-1]  # Get the innermost context
        context["security_risk"] = current.description
        context["security_severity"] = current.severity
    
    return context
