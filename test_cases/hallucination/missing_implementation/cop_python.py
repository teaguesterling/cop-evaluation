# Basic annotation library
# concept_python.py

def intent(description):
    """Document the intent of a function or class."""
    def decorator(obj):
        obj.__intent__ = description
        return obj
    return decorator

def invariant(condition_description):
    """Define an invariant that must be maintained."""
    def decorator(obj):
        if not hasattr(obj, '__invariants__'):
            obj.__invariants__ = []
        obj.__invariants__.append(condition_description)
        return obj
    return decorator

def human_decision(description, *, roles=None):
    """Mark a point where human judgment is required."""
    def decorator(func):
        func.__decision_point__ = True
        func.__decision_description__ = description
        func.__required_roles__ = roles
        return func
    return decorator

def ai_implement(description, *, constraints=None):
    """Mark a section implemented by AI with human-defined constraints."""
    def decorator(func):
        func.__ai_implemented__ = True
        func.__implementation_description__ = description
        func.__constraints__ = constraints or []
        return func
    return decorator
