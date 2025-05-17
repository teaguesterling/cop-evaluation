# cop_python/testing/verification.py
"""Verification utilities for COP testing."""

import inspect
from collections import defaultdict

# Registry for test verifications
_test_verifications = defaultdict(list)
_verification_failures = defaultdict(list)

def register_test_verification(test_func, verification_info):
    """
    Register that a test verifies a specific annotation.
    
    Args:
        test_func: The test function
        verification_info: Information about what's being verified
    """
    component = verification_info["component"]
    component_key = f"{component.__module__}.{verification_info['component_name']}"
    
    _test_verifications[component_key].append({
        "test": test_func.__name__,
        "test_module": test_func.__module__,
        "verification": verification_info
    })


def register_verification_failure(annotation_type, args, kwargs, exception):
    """
    Register a verification failure.
    
    Args:
        annotation_type: Type of annotation that failed verification
        args, kwargs: Arguments for the annotation
        exception: The exception that caused the failure
    """
    _verification_failures[annotation_type].append({
        "args": args,
        "kwargs": kwargs,
        "exception": str(exception)
    })


def check_component_test_coverage(component):
    """
    Check test coverage for all annotations on a component.
    
    Args:
        component: The component to check
        
    Returns:
        dict: Coverage information for the component
    """
    component_key = f"{component.__module__}.{component.__name__}"
    
    coverage = {
        "component": component.__name__,
        "invariants": [],
        "risks": [],
        "implementation_status": None,
        "decisions": []
    }
    
    # Check invariant coverage
    invariants = getattr(component, "__cop_invariants__", [])
    for inv in invariants:
        condition = inv["condition"] if isinstance(inv, dict) else inv
        tests = find_tests_for_invariant(component_key, condition)
        coverage["invariants"].append({
            "invariant": condition,
            "critical": inv.get("critical", False) if isinstance(inv, dict) else False,
            "tests": tests,
            "covered": len(tests) > 0
        })
    
    # Check risk coverage
    risks = getattr(component, "__cop_risks__", [])
    for risk in risks:
        description = risk["description"] if isinstance(risk, dict) else risk
        tests = find_tests_for_risk(component_key, description)
        coverage["risks"].append({
            "risk": description,
            "severity": risk.get("severity", "MEDIUM") if isinstance(risk, dict) else "MEDIUM",
            "tests": tests,
            "covered": len(tests) > 0
        })
    
    # Check implementation status
    status = getattr(component, "__cop_implementation_status__", None)
    if status:
        tests = find_tests_for_implementation_status(component_key, status)
        coverage["implementation_status"] = {
            "status": status,
            "tests": tests,
            "covered": len(tests) > 0
        }
    
    # Check decisions
    decisions = getattr(component, "__cop_decisions__", [])
    for decision in decisions:
        if isinstance(decision, dict):
            question = decision.get("question", "")
            tests = find_tests_for_decision(component_key, question)
            coverage["decisions"].append({
                "question": question,
                "answer": decision.get("answer", ""),
                "tests": tests,
                "covered": len(tests) > 0
            })
    
    return coverage


def find_tests_for_invariant(component_key, condition):
    """Find tests that verify a specific invariant."""
    tests = []
    
    for verification in _test_verifications[component_key]:
        if verification["verification"]["annotation_type"] == "invariant":
            if verification["verification"]["args"] and verification["verification"]["args"][0] == condition:
                tests.append(verification["test"])
    
    return tests


def find_tests_for_risk(component_key, description):
    """Find tests that verify a specific risk."""
    tests = []
    
    for verification in _test_verifications[component_key]:
        if verification["verification"]["annotation_type"] == "risk":
            if verification["verification"]["args"] and verification["verification"]["args"][0] == description:
                tests.append(verification["test"])
    
    return tests


def find_tests_for_implementation_status(component_key, status):
    """Find tests that verify implementation status."""
    tests = []
    
    for verification in _test_verifications[component_key]:
        if verification["verification"]["annotation_type"] == "implementation_status":
            if verification["verification"]["args"] and verification["verification"]["args"][0] == status:
                tests.append(verification["test"])
    
    return tests


def find_tests_for_decision(component_key, question):
    """Find tests that verify a specific decision."""
    tests = []
    
    for verification in _test_verifications[component_key]:
        if verification["verification"]["annotation_type"] == "decision":
            # Check args or kwargs for the question
            if verification["verification"]["args"] and question in str(verification["verification"]["args"]):
                tests.append(verification["test"])
            elif verification["verification"]["kwargs"].get("question") == question:
                tests.append(verification["test"])
    
    return tests


def generate_verification_report(module):
    """
    Generate a verification report for a module.
    
    Args:
        module: The module to analyze
        
    Returns:
        dict: Verification report
    """
    # Find all components with COP annotations
    components = []
    for name, obj in inspect.getmembers(module):
        if has_cop_annotations(obj):
            components.append(obj)
    
    # Check coverage for each component
    coverage_by_component = {}
    for component in components:
        coverage_by_component[component.__name__] = check_component_test_coverage(component)
    
    # Generate summary statistics
    summary = {
        "total_components": len(components),
        "components_with_tests": sum(1 for c in coverage_by_component.values() 
                                    if any(inv["covered"] for inv in c["invariants"]) or
                                       any(risk["covered"] for risk in c["risks"]) or
                                       (c["implementation_status"] and c["implementation_status"]["covered"]) or
                                       any(dec["covered"] for dec in c["decisions"])),
        "total_invariants": sum(len(c["invariants"]) for c in coverage_by_component.values()),
        "tested_invariants": sum(sum(1 for inv in c["invariants"] if inv["covered"]) 
                               for c in coverage_by_component.values()),
        "total_risks": sum(len(c["risks"]) for c in coverage_by_component.values()),
        "tested_risks": sum(sum(1 for risk in c["risks"] if risk["covered"]) 
                          for c in coverage_by_component.values()),
        "verification_failures": _verification_failures
    }
    
    return {
        "summary": summary,
        "coverage": coverage_by_component
    }


def has_cop_annotations(obj):
    """Check if an object has COP annotations."""
    return (hasattr(obj, "__cop_invariants__") or
            hasattr(obj, "__cop_risks__") or
            hasattr(obj, "__cop_implementation_status__") or
            hasattr(obj, "__cop_decisions__") or
            hasattr(obj, "__cop_intent__"))
