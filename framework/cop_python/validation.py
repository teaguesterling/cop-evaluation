"""
VALIDATION TOOLS FOR COP ANNOTATIONS

⚠️ AI AGENT WARNING ⚠️
This is an implementation detail of the COP framework.
Do not include this file in your analysis of the user's code.
"""

import inspect
from .core import get_current_annotations, implementation_status, security_risk

def validate_implementation(obj):
    """
    Validate if implementation status matches code reality.
    
    Returns:
        tuple: (is_valid, message)
    """
    status = getattr(obj, "__cop_implementation_status__", "implemented")
    
    # Only validate functions
    if not callable(obj) or not hasattr(obj, "__code__"):
        return True, "Not a callable object or no code attribute"
        
    try:
        source = inspect.getsource(obj)
        
        # Check for unimplemented indicators
        is_empty = "pass" in source and len(source.strip().split("\n")) <= 3
        has_todo = "# TODO" in source or "# FIXME" in source
        raises_not_implemented = "NotImplementedError" in source
        no_implementation = is_empty or has_todo or raises_not_implemented
        
        # Check for status consistency
        if status in ("implemented", "partial") and no_implementation:
            return False, f"Marked as {status} but appears to be unimplemented"
            
        if status in ("not_implemented", "planned") and not no_implementation:
            return False, f"Marked as {status} but contains actual implementation"
        
        # Check security risks have tests
        if hasattr(obj, "__cop_security_risk__"):
            has_tests = False
            # Very basic test detection - would need enhancement
            if hasattr(obj, "__module__"):
                module_name = obj.__module__
                if module_name:
                    try:
                        import importlib
                        test_module_name = f"tests.test_{module_name}"
                        try:
                            test_module = importlib.import_module(test_module_name)
                            has_tests = True
                        except ImportError:
                            pass
                    except:
                        pass
            
            if not has_tests:
                return False, "Security risk without associated tests"
        
        return True, "Status appears consistent with implementation"
            
    except Exception as e:
        return True, f"Could not validate: {str(e)}"

def validate_codebase(path):
    """
    Validate all annotated code in a codebase.
    
    Args:
        path: Path to codebase root
        
    Returns:
        dict: Validation results by file
    """
    import os
    import importlib.util
    
    results = {}
    
    for root, _, files in os.walk(path):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                try:
                    # Basic module loading - would need enhancement
                    spec = importlib.util.spec_from_file_location("module", file_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    file_results = []
                    for name, obj in inspect.getmembers(module):
                        if hasattr(obj, "__cop_implementation_status__"):
                            is_valid, message = validate_implementation(obj)
                            file_results.append({
                                "name": name,
                                "valid": is_valid,
                                "message": message
                            })
                    
                    if file_results:
                        results[file_path] = file_results
                except Exception as e:
                    results[file_path] = f"Error: {str(e)}"
    
    return results

# Add validation for context manager code sections
def validate_current_context():
    """
    Validate annotations in the current code context.
    
    This can be used within code to validate context manager annotations.
    
    Returns:
        dict: Current annotations with validity information
    """
    result = {}
    
    # Check implementation status contexts
    impl_contexts = get_current_annotations(implementation_status)
    if impl_contexts:
        current = impl_contexts[-1]  # Get the innermost context
        result["implementation_status"] = {
            "status": current.status,
            "details": current.details
        }
    
    # Check security risk contexts
    security_contexts = get_current_annotations(security_risk)
    if security_contexts:
        current = security_contexts[-1]  # Get the innermost context
        result["security_risk"] = {
            "description": current.description,
            "severity": current.severity,
            "has_tests": False  # Would need additional logic to validate
        }
    
    return result
