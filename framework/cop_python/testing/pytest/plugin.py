# cop_python/testing/integration/pytest_plugin.py
"""Pytest plugin for COP testing."""

import pytest
from ..verification import generate_verification_report

def pytest_configure(config):
    """Register COP markers."""
    config.addinivalue_line("markers", 
                           "cop_verify: verify COP annotations")


@pytest.fixture
def component_under_test(request):
    """Get the component being tested from test annotations."""
    
    # Find the first annotation that specifies a component
    for attr_name in dir(request.function):
        if attr_name.startswith("__cop_verifies_"):
            verification_info = getattr(request.function, attr_name)
            if "component" in verification_info:
                return verification_info["component"]
    
    # Default behavior if no component is found
    return None


@pytest.fixture(scope="session")
def cop_verification_report():
    """
    Fixture for generating COP verification reports.
    
    Usage:
        def test_something(cop_verification_report):
            report = cop_verification_report(my_module)
            # Use the report
    """
    def _generate_report(module):
        return generate_verification_report(module)
    
    return _generate_report


@pytest.hookimpl(trylast=True)
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Add COP verification summary to terminal report."""
    if hasattr(terminalreporter, "_cop_verification_results"):
        results = terminalreporter._cop_verification_results
        
        terminalreporter.write_sep("=", "COP Verification Summary")
        terminalreporter.write(f"Components tested: {results['summary']['total_components']}\n")
        terminalreporter.write(f"Components with tests: {results['summary']['components_with_tests']}\n")
        terminalreporter.write(f"Invariants: {results['summary']['tested_invariants']}/{results['summary']['total_invariants']}\n")
        terminalreporter.write(f"Security risks: {results['summary']['tested_risks']}/{results['summary']['total_risks']}\n")
        
        if results['summary']['verification_failures']:
            terminalreporter.write_sep("-", "Verification Failures")
            for anno_type, failures in results['summary']['verification_failures'].items():
                terminalreporter.write(f"{anno_type}: {len(failures)} failures\n")
