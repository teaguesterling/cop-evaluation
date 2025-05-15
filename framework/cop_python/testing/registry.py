"""
TEST REGISTRY SYSTEM FOR COP ANNOTATIONS

This module provides a registry system for linking tests directly
to COP annotations, particularly risks and invariants.
"""

import inspect
import functools
from typing import Dict, List, Any, Callable, Optional, Union, Set

class TestRegistry:
    """Registry tracking which tests cover which annotations."""
    
    # Structure:
    # {
    #   "module.function": {
    #     "risk": [
    #       {"test": "test_name", "details": {"type": "SECURITY", "description": "..."}},
    #       ...
    #     ],
    #     "invariant": [
    #       {"test": "test_name", "details": "Constraint description"},
    #       ...
    #     ]
    #   }
    # }
    _mappings = {}
    
    # Set of tests that have been executed
    _executed_tests = set()
    
    @classmethod
    def register(cls, test_func: Callable, module: str, function: Optional[str] = None, **annotations) -> None:
        """
        Register a test as covering specific annotations.
        
        Args:
            test_func: The test function being registered
            module: The module being tested
            function: The specific function being tested (optional)
            **annotations: Annotation mappings (risk, invariant, etc.)
        """
        component_key = f"{module}.{function}" if function else module
        
        if component_key not in cls._mappings:
            cls._mappings[component_key] = {}
            
        for annotation_type, annotation_details in annotations.items():
            if annotation_type not in cls._mappings[component_key]:
                cls._mappings[component_key][annotation_type] = []
                
            # Add the test to the registry
            cls._mappings[component_key][annotation_type].append({
                "test": test_func.__name__,
                "test_func": test_func,
                "details": annotation_details,
                "source": getattr(test_func, "__module__", "unknown")
            })
    
    @classmethod
    def mark_executed(cls, test_name: str) -> None:
        """Mark a test as having been executed."""
        cls._executed_tests.add(test_name)
    
    @classmethod
    def get_tests_for_component(cls, module: str, function: Optional[str] = None) -> Dict[str, List[Dict]]:
        """
        Get all tests for a component.
        
        Args:
            module: The module name
            function: The specific function name (optional)
            
        Returns:
            Dict mapping annotation types to lists of tests
        """
        component_key = f"{module}.{function}" if function else module
        return cls._mappings.get(component_key, {})
    
    @classmethod
    def get_tests_for_annotation(cls, module: str, function: str, annotation_type: str, **criteria) -> List[Dict]:
        """
        Get tests that verify a specific annotation.
        
        Args:
            module: The module name
            function: The function name
            annotation_type: The type of annotation (risk, invariant, etc.)
            **criteria: Criteria to filter tests
            
        Returns:
            List of matching tests
        """
        component_key = f"{module}.{function}"
        component_tests = cls._mappings.get(component_key, {})
        
        if annotation_type not in component_tests:
            return []
            
        tests = component_tests[annotation_type]
        
        # Filter by criteria if provided
        if criteria:
            filtered_tests = []
            for test in tests:
                details = test.get("details", {})
                if isinstance(details, dict):
                    # Check if all criteria match
                    if all(details.get(k) == v for k, v in criteria.items()):
                        filtered_tests.append(test)
                else:
                    # For string details, simple equality check
                    if details == next(iter(criteria.values()), None):
                        filtered_tests.append(test)
            return filtered_tests
        
        return tests
    
    @classmethod
    def get_executed_tests_for_annotation(cls, module: str, function: str, annotation_type: str, **criteria) -> List[Dict]:
        """
        Get executed tests that verify a specific annotation.
        
        Args:
            module: The module name
            function: The function name
            annotation_type: The type of annotation (risk, invariant, etc.)
            **criteria: Criteria to filter tests
            
        Returns:
            List of matching executed tests
        """
        tests = cls.get_tests_for_annotation(module, function, annotation_type, **criteria)
        return [test for test in tests if test["test"] in cls._executed_tests]
    
    @classmethod
    def get_all_components(cls) -> List[str]:
        """Get all registered components."""
        return list(cls._mappings.keys())
    
    @classmethod
    def get_untested_annotations(cls, module: str, function: Optional[str] = None, annotation_type: Optional[str] = None) -> List[Dict]:
        """
        Get all untested annotations for a component.
        
        Args:
            module: The module name
            function: The specific function name (optional)
            annotation_type: The specific annotation type (optional)
            
        Returns:
            List of untested annotations
        """
        import importlib
        import inspect
        
        # Try to load the module
        try:
            mod = importlib.import_module(module)
        except ImportError:
            return [{"error": f"Could not import module {module}"}]
        
        untested = []
        
        # If function specified, check just that function
        if function:
            try:
                func = getattr(mod, function)
                untested.extend(cls._get_untested_annotations_for_object(
                    func, module, function, annotation_type
                ))
            except AttributeError:
                return [{"error": f"Could not find function {function} in module {module}"}]
            
            return untested
        
        # Otherwise check all objects in the module
        for name, obj in inspect.getmembers(mod):
            if name.startswith("_"):
                continue
                
            untested.extend(cls._get_untested_annotations_for_object(
                obj, module, name, annotation_type
            ))
        
        return untested
    
    @classmethod
    def _get_untested_annotations_for_object(cls, obj: Any, module: str, name: str, annotation_type: Optional[str] = None) -> List[Dict]:
        """Helper method to get untested annotations for an object."""
        untested = []
        
        # Check all annotation types or just the specified one
        types_to_check = [annotation_type] if annotation_type else ["risk", "invariant"]
        
        # Check for risks
        if "risk" in types_to_check and hasattr(obj, "__cop_risks__"):
            risks = getattr(obj, "__cop_risks__", [])
            for risk in risks:
                risk_type = risk.get("type", "SECURITY")
                description = risk.get("description", "")
                severity = risk.get("severity", "HIGH")
                
                # Look for tests covering this risk
                tests = cls.get_executed_tests_for_annotation(
                    module, name, "risk",
                    type=risk_type, description=description
                )
                
                if not tests:
                    untested.append({
                        "component": f"{module}.{name}",
                        "annotation_type": "risk",
                        "type": risk_type,
                        "description": description,
                        "severity": severity
                    })
        
        # Check for invariants
        if "invariant" in types_to_check and hasattr(obj, "__cop_invariants__"):
            invariants = getattr(obj, "__cop_invariants__", [])
            for invariant in invariants:
                # Handle both string and dict formats
                if isinstance(invariant, dict):
                    condition = invariant.get("condition", "")
                    inv_type = invariant.get("type", None)
                else:
                    condition = invariant
                    inv_type = None
                
                # Look for tests covering this invariant
                tests = cls.get_executed_tests_for_annotation(
                    module, name, "invariant", condition=condition
                )
                
                if not tests:
                    untested.append({
                        "component": f"{module}.{name}",
                        "annotation_type": "invariant",
                        "condition": condition,
                        "type": inv_type
                    })
        
        return untested


def test_for(module: str, function: Optional[str] = None, **annotations):
    """
    Decorator to mark a test as covering specific annotations.
    
    Args:
        module: The module being tested
        function: The specific function being tested (optional)
        **annotations: Annotation mappings (risk, invariant, etc.)
        
    Example:
        @test_for("payment_processor", "process_payment", 
                 risk={"type": "SECURITY", "description": "PCI compliance"})
        def test_payment_security():
            # Test implementation
    """
    def decorator(test_func):
        # Register this test
        TestRegistry.register(test_func, module, function, **annotations)
        
        @functools.wraps(test_func)
        def wrapper(*args, **kwargs):
            # Run the test
            result = test_func(*args, **kwargs)
            
            # Mark as executed
            TestRegistry.mark_executed(test_func.__name__)
            
            return result
        
        return wrapper
    
    return decorator
