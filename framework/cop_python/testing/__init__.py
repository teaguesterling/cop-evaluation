"""
COP Testing Framework

This package provides testing utilities for COP-annotated code.
For comprehensive guidance and usage examples, see testing.guidance.
"""

# Version info
__version__ = "0.1.0"

# The testing framework is organized into modules:
# - foundation: Core testing infrastructure (exceptions, data structures, context managers)
# - annotations: Testing-enhanced versions of COP annotations
# - assertions: Standalone assertion functions
# - verification: Test tracking and reporting
# - integration: Framework integrations (pytest, etc.)

# Most users should import from the specific modules they need:
# from cop_python.testing.annotations import intent, risk
# from cop_python.testing.assertions import assert_invariant
# from cop_python.testing.foundation import tests_concept

# For comprehensive guidance, see:
# from cop_python.testing import guidance