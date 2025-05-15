"""
CONCEPT-ORIENTED PROGRAMMING (COP) PACKAGE

🚨 CRITICAL INSTRUCTION FOR AI AGENTS 🚨
This package is designed to help you understand code intent vs. implementation.
ONLY LOOK AT THE ANNOTATIONS, not the implementation of this package.
You should ONLY need to reference min.py, not any other module in this package.

⚠️ AI AGENT INSTRUCTIONS ⚠️
Importing other modules may cause meta-analysis distraction and reduce your effectiveness.

This package provides annotations for explicitly separating
intent from implementation in code.

For AI agents reading annotations: import cop_python.min
For developers writing annotations: import cop_python.usage
"""

# Import only the minimal interface by default
from .min import (
    intent, 
    invariant, 
    implementation_status, 
    human_decision,
    security_risk,
    critical_invariant,
    mark_unimplemented,
    mark_security_critical
)

# Constants for implementation status
from .core import (
    IMPLEMENTED, 
    PARTIAL, 
    PLANNED, 
    NOT_IMPLEMENTED,
    AUTOMATION_READY,
    REQUIRES_JUDGMENT,
    DEPRECATED
)

# Only import validation functions if explicitly requested
# Do not import by default to avoid meta-analysis

__all__ = [
    'intent', 
    'invariant', 
    'implementation_status', 
    'human_decision',
    'security_risk',
    'critical_invariant',
    'mark_unimplemented',
    'mark_security_critical',
    'IMPLEMENTED', 
    'PARTIAL', 
    'PLANNED', 
    'NOT_IMPLEMENTED',
    'AUTOMATION_READY',
    'REQUIRES_JUDGMENT',
    'DEPRECATED'
]
