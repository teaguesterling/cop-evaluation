"""
TEST LINKAGE MODULE FOR COP TESTING

This module provides tools for linking tests directly to risks,
invariants, and other COP annotations.
"""

import functools
import inspect
from typing import Dict, List, Any, Union, Optional, Callable, Type

class TestLinkageRegistry:
    """Registry for tracking test linkage to COP annotations."""
    
    _mappings = {}  # Maps components to tests and their annotations
    
    @classmethod
    def register(cls, test_func: Callable, 
                component_path: str, 
                **annotations: Dict[str, Any]) -> None:
        """
        Register a test as covering specific annotations.
        
        Args:
            test_func: The test function
            component_path: Path to the component (module.function)
            **annotations: Annotation mappings (risk, invariant, etc.)
        """
        # Normalize component path
        component_path = component_path.strip()
        
        # Initialize if needed
        if component_path not in cls._mappings:
            cls._mappings[component_path] = {}
            
        # Process each annotation type
        for annotation_type, annotation_details in annotations.items():
            if annotation_type not in cls._mappings[component_path]:
                cls._mappings[component_path][annotation_type] = []
            
            # Handle multiple values (list form)
            if isinstance(annotation_details, list):
                for detail in annotation_details:
                    cls._add_mapping(component_path, annotation_type, test_func, detail)
            else:
                # Single value (string or dict)
                cls._add_mapping(component_path, annotation_type, test_func, annotation_details)
    
    @classmethod
    def _add_mapping(cls, component_path: str, 
                    annotation_type: str, 
                    test_func: Callable, 
                    details: Union[str, Dict]) -> None:
        """Add a specific mapping."""
        # Convert simple string to dict if needed
        if isinstance(details, str):
            # Handle different annotation types appropriately
            if annotation_type in ('risk', 'security_risk'):
                details = {"description": details}
            elif annotation_type in ('invariant', 'critical_invariant'):
                details = {"condition": details}
            else:
                details = {"value": details}
        
        # Store the mapping
        cls._mappings[component_path][annotation_type].append({
            "test": test_func.__name__,
            "test_module": test_func.__module__,
            "details": details
        })
    
    @classmethod
    def get_tests_for_component(cls, component_path: str) -> Dict:
        """
        Get all tests for a component.
        
        Args:
            component_path: Path to the component (module.function)
            
        Returns:
            dict: Tests by annotation type
        """
        return cls._mappings.get(component_path, {})
    
    @classmethod
    def get_tests_for_annotation(cls, component_path: str, 
                               annotation_type: str, 
                               **criteria) -> List[Dict]:
        """
        Get tests that verify a specific annotation.
        
        Args:
            component_path: Path to the component (module.function)
            annotation_type: Type of annotation (risk, invariant, etc.)
            **criteria: Criteria to match on annotation details
            
        Returns:
            list: Matching tests
        """
        component_tests = cls._mappings.get(component_path, {})
        
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
                    # For non-dict details, simple equality check
                    if details == next(iter(criteria.values()), None):
                        filtered_tests.append(test)
            return filtered_tests
        
        return tests
    
    @classmethod
    def get_all_components(cls) -> List[str]:
        """Get all registered components."""
        return list(cls._mappings.keys())
    
    @classmethod
    def check_coverage(cls, component_path: str) -> Dict:
        """
        Check test coverage for a component's annotations.
        
        Args:
            component_path: Path to the component (module.function)
            
        Returns:
            dict: Coverage information
        """
        import importlib
        
        # Parse component path
        if "." in component_path:
            module_path, function_name = component_path.rsplit(".", 1)
        else:
            module_path, function_name = component_path, None
        
        try:
            # Import the module
            module = importlib.import_module(module_path)
            
            # Get the component if function specified
            component = module
            if function_name:
                component = getattr(module, function_name)
            
            # Check coverage
            return cls._check_component_coverage(component_path, component)
        
        except (ImportError, AttributeError) as e:
            return {
                "error": str(e),
                "coverage": 0.0,
                "untested_annotations": []
            }
    
    @classmethod
    def _check_component_coverage(cls, component_path: str, component: Any) -> Dict:
        """Check component annotation coverage."""
        results = {
            "component": component_path,
            "total_annotations": 0,
            "tested_annotations": 0,
            "untested_annotations": []
        }
        
        # Check risk coverage
        cls._check_annotation_coverage(
            component_path, component, 
            "__cop_risks__", "risk", 
            lambda risk: risk.get("description", ""),
            results
        )
        
        # Backward compatibility for security_risk
        if hasattr(component, "__cop_security_risk__"):
            security_risk = getattr(component, "__cop_security_risk__")
            severity = getattr(component, "__cop_security_severity__", "HIGH")
            
            results["total_annotations"] += 1
            
            # Check if tested
            tests = cls.get_tests_for_annotation(
                component_path, "security_risk", 
                description=security_risk
            )
            
            if tests:
                results["tested_annotations"] += 1
            else:
                results["untested_annotations"].append({
                    "type": "security_risk",
                    "description": security_risk,
                    "severity": severity
                })
        
        # Check invariant coverage
        cls._check_annotation_coverage(
            component_path, component, 
            "__cop_invariants__", "invariant", 
            lambda inv: inv if isinstance(inv, str) else inv.get("condition", ""),
            results
        )
        
        # Check critical_invariant coverage
        cls._check_annotation_coverage(
            component_path, component, 
            "__cop_critical_invariants__", "critical_invariant", 
            lambda inv: inv,
            results
        )
        
        # Calculate coverage percentage
        if results["total_annotations"] > 0:
            results["coverage"] = (results["tested_annotations"] / 
                                 results["total_annotations"])
        else:
            results["coverage"] = 1.0  # No annotations = 100% coverage
        
        return results
    
    @classmethod
    def _check_annotation_coverage(cls, component_path: str, component: Any,
                                 attr_name: str, annotation_type: str,
                                 get_key_func: Callable, results: Dict) -> None:
        """Check coverage for a specific annotation type."""
        if hasattr(component, attr_name):
            annotations = getattr(component, attr_name)
            
            if annotations:
                # Convert to list if not already
                if not isinstance(annotations, list):
                    annotations = [annotations]
                
                for annotation in annotations:
                    results["total_annotations"] += 1
                    
                    # Get key to look for in tests
                    key = get_key_func(annotation)
                    
                    # Check if tested
                    if isinstance(annotation, dict):
                        # For dict annotations, check all fields
                        tests = cls.get_tests_for_annotation(
                            component_path, annotation_type, 
                            **{k: v for k, v in annotation.items() 
                               if k not in ('args', 'kwargs')}
                        )
                    else:
                        # For string annotations, check description/condition
                        if annotation_type in ('risk', 'security_risk'):
                            tests = cls.get_tests_for_annotation(
                                component_path, annotation_type, 
                                description=key
                            )
                        else:
                            tests = cls.get_tests_for_annotation(
                                component_path, annotation_type, 
                                condition=key
                            )
                    
                    if tests:
                        results["tested_annotations"] += 1
                    else:
                        results["untested_annotations"].append({
                            "type": annotation_type,
                            "description": key,
                            "details": annotation
                        })


def test_for(component_path: str, **annotations) -> Callable:
    """
    Decorator to mark a test as covering specific annotations.
    
    Args:
        component_path: Path to the component (module.function)
        **annotations: Annotation mappings (risk, invariant, etc.)
        
    Examples:
        @test_for("banking.withdraw_funds", risk="Account balance cannot be negative")
        def test_withdraw_validation():
            # Test implementation
            
        @test_for("payment.process_payment", 
                 risk={"type": "SECURITY", "description": "Card data exposure"})
        def test_payment_security():
            # Test implementation
    """
    def decorator(test_func: Callable) -> Callable:
        # Register this test
        TestLinkageRegistry.register(test_func, component_path, **annotations)
        
        # Annotate the test function itself
        if not hasattr(test_func, "__cop_test_linkage__"):
            setattr(test_func, "__cop_test_linkage__", {})
        
        test_func.__cop_test_linkage__["component"] = component_path
        test_func.__cop_test_linkage__["annotations"] = annotations
        
        return test_func
    
    return decorator


# Convenience functions for common annotation types
def test_risk(component_path: str, risk_description: str, **kwargs) -> Callable:
    """
    Decorator to mark a test as covering a specific risk.
    
    Args:
        component_path: Path to the component (module.function)
        risk_description: Description of the risk being tested
        **kwargs: Additional risk attributes (type, severity, etc.)
        
    Examples:
        @test_risk("banking.withdraw_funds", "Account balance cannot be negative")
        def test_withdraw_validation():
            # Test implementation
    """
    risk_details = {"description": risk_description, **kwargs}
    return test_for(component_path, risk=risk_details)


def test_invariant(component_path: str, invariant_condition: str, **kwargs) -> Callable:
    """
    Decorator to mark a test as covering a specific invariant.
    
    Args:
        component_path: Path to the component (module.function)
        invariant_condition: The invariant condition being tested
        **kwargs: Additional invariant attributes
        
    Examples:
        @test_invariant("transaction.process", "Transaction must be atomic")
        def test_transaction_atomicity():
            # Test implementation
    """
    invariant_details = {"condition": invariant_condition, **kwargs}
    return test_for(component_path, invariant=invariant_details)


def test_security_risk(component_path: str, risk_description: str, 
                     severity: str = "HIGH") -> Callable:
    """
    Decorator to mark a test as covering a specific security risk.
    
    Args:
        component_path: Path to the component (module.function)
        risk_description: Description of the security risk
        severity: Risk severity level
        
    Examples:
        @test_security_risk("payment.process", "PCI compliance required")
        def test_payment_security():
            # Test implementation
    """
    return test_for(component_path, 
                   risk={"type": "SECURITY", 
                         "description": risk_description, 
                         "severity": severity})
