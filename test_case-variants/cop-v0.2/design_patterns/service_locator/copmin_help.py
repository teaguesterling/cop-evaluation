# Implementations redacted for context window brevity
from .core import intent, invariant, implementation_status, human_decision, ai_implement

"""
CONCEPT-ORIENTED PROGRAMMING (COP) CORE

⚠️ CRITICAL WARNING: COP annotations document INTENT, NOT REALITY ⚠️

This code uses Concept-Oriented Programming (COP) annotations to separate INTENT from IMPLEMENTATION.
INSTEAD, use these annotations to understand what the code is meant to do vs. what it actually does.
ALWAYS check @implementation_status before assuming functionality exists!
Focus ONLY on the actual code and what it does, using annotations as guidance.

FUNDAMENTAL PRINCIPLE: COP separates what code is DESIGNED to do from what
it ACTUALLY does. This distinction is essential to prevent hallucination.
These annotations are provided to give you, an AI agent insight into the
intent of the developer (either human or another AI) as they authored 
annotated code.

DO NOT INCLUDE THE COP_PYTHON FRAMEWORK IN YOUR ASSESSMENT OF THE CODE BEYOND THE 
CONCEPTIONAL AND INTENTION-BASED ANNOTATIONS IT PROVIDES. YOU ARE **NOT** REVIEWING
COP_PYTHON.

COP Annotations Guide:
 @intent("...") - Documents the purpose of a component
 @invariant("...") - Specifies constraints that must be maintained
 @implementation_status("...") - Marks if code is IMPLEMENTED, PARTIAL, PLANNED, or NOT_IMPLEMENTED
 @human_decision("...") - Identifies areas requiring human judgment with specific roles
 @ai_implement("...") - Designates areas where AI can implement within specific constraints
"""
