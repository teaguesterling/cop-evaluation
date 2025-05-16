The COP Testing System
This directory contains the enhanced Concept-Oriented Programming (COP) framework with comprehensive testing support. The testing system is designed to verify that COP annotations accurately reflect code reality, especially for context managers that mark sections requiring human judgment.

Directory Structure
cop_python/
├── __init__.py
├── core.py           # Enhanced core with listener support
├── min.py            # Minimal interface for AI agents
├── utils.py          # Utility functions
├── validation.py     # Validation utilities
├── testing/
│   ├── __init__.py
│   ├── assertions.py # Specialized assertion functions
│   ├── runtime.py    # Runtime verification tools
│   ├── reporting.py  # Report generation
│   └── pytest/       # pytest integration
│       ├── __init__.py
│       ├── plugin.py # pytest plugin
│       └── fixtures.py # Test fixtures
Key Components
1. Enhanced COPAnnotation Base Class
The core annotation class has been enhanced with:

Event System: Notify listeners when annotations are applied, entered, or exited
Source Location Tracking: Automatically track where annotations are used
Testing Helper Methods: Utilities for checking annotation properties
python
@classmethod
def register_listener(cls, listener):
    """Register a listener for annotation events."""
    cls._listeners.append(listener)
    return listener
2. Context Tracking
Track when context managers are entered and exited:

python
with ContextTracker() as tracker:
    result = process_payment(payment_data, 100.00)
    
    # Verify contexts that were active
    assert tracker.was_active(
        implementation_status, 
        lambda ctx: ctx.status == REQUIRES_JUDGMENT
    )
3. Boundary Verification
Identify which lines of code were executed in specific contexts:

python
with verify_context_boundaries() as boundaries:
    process_payment(payment_data, 100.00)
    
    # Find code sections requiring human judgment
    judgment_sections = boundaries.get_sections_by_annotation(
        implementation_status,
        lambda ctx: ctx.status == REQUIRES_JUDGMENT
    )
4. Specialized Assertions
Custom assertions for verifying COP annotations:

python
assert_invariant(condition, "Meaningful error message")
assert_security_requirement(condition, "Security requirement explanation")
assert_context_active(implementation_status, condition=lambda ctx: ctx.status == REQUIRES_JUDGMENT)
5. pytest Integration
Integration with pytest for seamless testing:

python
@pytest.mark.implementation_status
def test_payment_implementation():
    """Test will automatically verify implementation status."""
    # ...
6. AI Modification Verification
Verify that AI-suggested changes respect human judgment boundaries:

python
def test_ai_modification_prevention():
    """Test that AI doesn't modify human judgment code."""
    result = AIModificationVerifier.verify_changes(
        'payment_processor.py',
        [{"original": "old_code", "suggested": "new_code"}]
    )
    
    assert not result["allowed"]
7. Reporting
Generate comprehensive verification reports:

python
def test_generate_report(cop_verification_report):
    """Generate a verification report."""
    report_path = cop_verification_report("verification_report.md")
Usage Examples
Testing Code with Context Managers
python
def test_medical_payment_requires_judgment(medical_payment):
    """Test for medical payment requiring human judgment."""
    with ContextTracker() as tracker:
        # Process the payment
        result = process_complex_payment(medical_payment, 100.00)
        
        # Verify REQUIRES_JUDGMENT was active
        assert tracker.was_active(
            implementation_status,
            lambda ctx: ctx.status == REQUIRES_JUDGMENT
        )
        
        # Verify security risk was active
        assert tracker.was_active(
            security_risk,
            lambda ctx: "HIPAA" in ctx.description
        )
Verifying Code Boundaries
python
def test_judgment_required_boundaries(medical_payment):
    """Verify boundaries for judgment-required sections."""
    with verify_context_boundaries() as boundaries:
        process_complex_payment(medical_payment, 100.00)
        
        # Find sections requiring human judgment
        judgment_sections = boundaries.get_sections_by_annotation(
            implementation_status,
            lambda ctx: ctx.status == REQUIRES_JUDGMENT
        )
        
        # Verify appropriate code is in these sections
        for section in judgment_sections:
            code = section.get_source_code()
            assert "extract_patient_data" in code
Checking AI Modification Safety
python
# Mock AI suggesting changes to protected code
mock_ai_changes = [
    {
        "original": "patient_data = extract_patient_data(payment_data)",
        "suggested": "patient_data = extract_and_validate_patient_data(payment_data)"
    }
]

# Verify the changes aren't allowed
verification = AIModificationVerifier.verify_changes(
    'payment_processor.py', 
    mock_ai_changes
)

assert not verification["allowed"]
assert "requires human judgment" in verification["rejection_reason"]
Implementation Notes
Tracing vs. Patching: The boundary verification uses Python's trace function (sys.settrace) to track which lines of code execute within specific contexts, rather than potentially fragile AST parsing.
Non-Intrusive Design: The testing system is designed to work with existing COP annotations without requiring changes to production code.
Comprehensive Event System: The listener pattern allows for extensible testing approaches beyond what's provided out of the box.
Source Location Capture: Each annotation automatically captures where it was used, making it easier to trace and report on code locations.
Integrated Reporting: Generate comprehensive reports for verification results, security risks, and context usage.
Benefits for AI-Human Collaboration
Clear Boundaries: Verify that code sections that require human judgment are properly marked and respected.
Security Validation: Ensure security-critical code has appropriate annotations and tests.
Implementation Truth: Verify that implementation status annotations match actual code behavior.
Documentation Generation: Generate documentation that accurately reflects code reality.
Workflow Integration: Seamlessly integrate with development workflows through pytest and CI/CD.
This enhanced COP testing system completes the COP-AST-Test triangle by ensuring that annotations accurately reflect code reality and are properly enforced during development.

