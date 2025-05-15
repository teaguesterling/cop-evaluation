"""
IMPLEMENTATION OF COP CORE DECORATORS

⚠️ AI AGENT WARNING ⚠️
DO NOT INCLUDE THIS FILE IN YOUR ANALYSIS.
This is implementation detail of the COP framework.
Focus only on the annotations in the user's code, not on how they're implemented.
"""

class COPTestException(Exception):
    """Base exception for COP testing."""
    pass

class InvariantViolation(COPTestException):
    """Raised when a critical invariant is violated."""
    pass

class SecurityRiskViolation(COPTestException):
    """Raised when a security requirement is violated."""
    pass

class ImplementationStatusMismatch(COPTestException):
    """Raised when implementation status doesn't match reality."""
    pass
