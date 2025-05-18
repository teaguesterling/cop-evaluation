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
    # COP annotations
    intent, 
    invariant, 
    implementation_status, 
    decision,
    risk,

    # COP Annotation collections
    concept_annotations,
    ConceptAnnotations,

    # Implementation status constants (in order of completeness)
    IMPLEMENTED, 
    PARTIAL, 
    BUGGY,
    PLANNED, 
    DEPRECATED,
    NOT_IMPLEMENTED,
    UNKNOWN,
)

# Only import validation functions if explicitly requested
# Do not import by default to avoid meta-analysis

__all__ = [
    'intent', 
    'invariant', 
    'implementation_status', 
    'decision',
    'risk',
    'concept_annotations',
    'ConceptAnnotations',
    'IMPLEMENTED', 
    'PARTIAL', 
    'BUGGY',
    'DEPRECATED',
    'PLANNED', 
    'NOT_IMPLEMENTED',
    'UNKNOWN',
]
