"""
TESTING MODULE INIT FILE

Exposes key testing functionality for COP annotations.
"""

# Import core testing components
from .testing import (
    ContextTracker, 
    verify_context_boundaries,
    TestingException,
    ContextVerificationError
)

# Import assertions
from .assertions import (
    assert_invariant,
    assert_security_requirement,
    assert_implementation_matches_status,
    assert_context_active,
    InvariantViolation,
    SecurityRiskViolation,
    ImplementationStatusMismatch
)

# Import registry functions
from .registry import test_for, TestRegistry

# Import verification helpers
from .verification import (
    verify_implementation,
    verify_risk_coverage,
    verify_invariant_coverage,
    VerificationResult
)

# Pytest integration is imported automatically when pytest is used

__all__ = [
    # Core testing
    'ContextTracker',
    'verify_context_boundaries',
    'TestingException',
    'ContextVerificationError',
    
    # Assertions
    'assert_invariant',
    'assert_security_requirement',
    'assert_implementation_matches_status',
    'assert_context_active',
    'InvariantViolation',
    'SecurityRiskViolation',
    'ImplementationStatusMismatch',
    
    # Registry
    'test_for',
    'TestRegistry',
    
    # Verification
    'verify_implementation',
    'verify_risk_coverage',
    'verify_invariant_coverage',
    'VerificationResult'
]
