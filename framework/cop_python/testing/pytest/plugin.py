"""
PYTEST INTEGRATION FOR COP TESTING

This module provides pytest fixtures, hooks, and markers for
integrating COP testing with pytest.
"""

import os
import sys
import pytest
from typing import List, Dict, Any, Callable, Optional

from ..core import COPAnnotation, implementation_status, security_risk
from ..testing import ContextTracker, verify_context_boundaries, TestingException

# Register custom markers
def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line("markers", 
                           "implementation_status: verify implementation status")
    config.addinivalue_line("markers", 
                           "security: verify security requirements")
    config.addinivalue_line("markers", 
                           "invariants: verify critical invariants")
    config.addinivalue_line("markers", 
                           "context_tracking: track COP contexts during test")

# Global tracker for collecting context information across all tests
class GlobalContextCollector:
    """Collect context information across multiple tests."""
    
    def __init__(self):
        self.contexts = []
        self.violations = []
        self.covered_components = set()
    
    def add_contexts(self, contexts):
        """Add contexts from a test run."""
        self.contexts.extend(contexts)
    
    def add_violation(self, component, violation_type, details):
        """Record a COP violation."""
        self.violations.append({
            "component": component,
            "test": context.get_current_test(),
            "type": violation_type,
            "details": details
        })
    
    def add_component(self, component):
        """Record that a component was covered by tests."""
        self.covered_components.add(component)
    
    def clear(self):
        """Clear all collected data."""
        self.contexts = []
        self.violations = []
        self.covered_components = set()

# Create a global collector
_global_collector = GlobalContextCollector()

# Get a clean collector for each test session
@pytest.fixture(scope="session", autouse=True)
def global_context_collector():
    """Provide a global context collector for the session."""
    _global_collector.clear()
    return _global_collector

# Track the current test
_current_test = None

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """Set up the current test in the verification context."""
    global _current_test
    _current_test = item.nodeid

@pytest.hookimpl(trylast=True)
def pytest_runtest_teardown(item):
    """Clean up after each test."""
    global _current_test
    _current_test = None

def get_current_test():
    """Get the current running test."""
    return _current_test

# Context tracking fixture
@pytest.fixture
def context_tracker():
    """Fixture for tracking COP contexts during a test."""
    with ContextTracker() as tracker:
        yield tracker
        # Add contexts to global collection after test
        _global_collector.add_contexts(tracker.contexts)

# Boundary verification fixture
@pytest.fixture
def boundary_tracker():
    """Fixture for tracking code section boundaries."""
    with verify_context_boundaries() as tracker:
        yield tracker

# Combined tracking fixture
@pytest.fixture
def cop_tracker():
    """Combined fixture for both context and boundary tracking."""
    with ContextTracker() as ctx_tracker:
        with verify_context_boundaries() as boundary_tracker:
            yield {
                "context": ctx_tracker,
                "boundaries": boundary_tracker
            }
        # Add contexts to global collection after test
        _global_collector.add_contexts(ctx_tracker.contexts)

# Report generation fixture
@pytest.fixture
def cop_verification_report():
    """Fixture to generate a verification report."""
    def _generate_report(output_path=None):
        """Generate a verification report."""
        from ..reporting import generate_verification_report
        
        report = generate_verification_report(
            _global_collector.violations,
            _global_collector.covered_components,
            _global_collector.contexts,
            output_path
        )
        
        return report
    
    return _generate_report

# Terminal summary hook
@pytest.hookimpl(trylast=True)
def pytest_terminal_summary(terminalreporter):
    """Add COP verification summary to pytest output."""
    if _global_collector.violations:
        terminalreporter.write_sep("=", "COP Verification Issues")
        for violation in _global_collector.violations:
            component_name = (
                violation['component'].__name__ 
                if hasattr(violation['component'], '__name__') 
                else str(violation['component'])
            )
            terminalreporter.write(
                f"{component_name}: {violation['type']} - {violation['details']}\n"
            )
    
    # Add context statistics
    contexts_by_type = {}
    for ctx in _global_collector.contexts:
        type_name = ctx.annotation_type.__name__
        if type_name not in contexts_by_type:
            contexts_by_type[type_name] = 0
        contexts_by_type[type_name] += 1
    
    if contexts_by_type:
        terminalreporter.write_sep("=", "COP Context Coverage")
        for ctx_type, count in contexts_by_type.items():
            terminalreporter.write(f"{ctx_type}: {count} occurrences\n")
