import pytest
from ..verification import (
    VerificationResult, register_test_verification, 
    record_verification_result, set_up_test_run,
    finish_test_run, generate_verification_report
)
from ...utils import COPAnnotationReference

def pytest_configure(config):
    """Register COP markers and set up verification."""
    config.addinivalue_line("markers", 
                           "cop_verify: verify COP annotations")
    set_up_test_run()

def pytest_unconfigure(config):
    """Generate verification report at end of test run."""
    report = finish_test_run()
    # Could save the report to a file here if desired

@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """Set up COP verification for a test."""
    # Find annotation verifications from test
    for attr_name in dir(item.obj):
        if attr_name.startswith("__cop_verifies_"):
            verification_info = getattr(item.obj, attr_name)
            annotation_type = verification_info.get("annotation_type")
            component = verification_info.get("component")
            args = verification_info.get("args", [])
            kwargs = verification_info.get("kwargs", {})
            
            if component and annotation_type:
                # Create annotation reference
                annotation_reference = COPAnnotationReference(
                    annotation_type=annotation_type,
                    annotation_value=args[0] if args else None,
                    metadata_keys=kwargs
                )
                
                # Register verification
                register_test_verification(
                    item.obj, 
                    component, 
                    annotation_reference
                )

@pytest.hookimpl(trylast=True)
def pytest_runtest_call(item):
    """Record verification result after test runs."""
    for attr_name in dir(item.obj):
        if attr_name.startswith("__cop_verifies_"):
            verification_info = getattr(item.obj, attr_name)
            annotation_type = verification_info.get("annotation_type")
            component = verification_info.get("component")
            args = verification_info.get("args", [])
            kwargs = verification_info.get("kwargs", {})
            
            if component and annotation_type:
                # Create annotation reference
                annotation_reference = COPAnnotationReference(
                    annotation_type=annotation_type,
                    annotation_value=args[0] if args else None,
                    metadata_keys=kwargs
                )
                
                # Record result as passed (no error occurred)
                record_verification_result(
                    item.obj,
                    component,
                    annotation_reference,
                    VerificationResult.PASSED
                )

@pytest.hookimpl(trylast=True)
def pytest_runtest_makereport(item, call):
    """Record verification failure if test fails."""
    if call.excinfo is not None:
        for attr_name in dir(item.obj):
            if attr_name.startswith("__cop_verifies_"):
                verification_info = getattr(item.obj, attr_name)
                annotation_type = verification_info.get("annotation_type")
                component = verification_info.get("component")
                args = verification_info.get("args", [])
                kwargs = verification_info.get("kwargs", {})
                
                if component and annotation_type:
                    # Create annotation reference
                    annotation_reference = COPAnnotationReference(
                        annotation_type=annotation_type,
                        annotation_value=args[0] if args else None,
                        metadata_keys=kwargs
                    )
                    
                    # Record result as failed
                    record_verification_result(
                        item.obj,
                        component,
                        annotation_reference,
                        VerificationResult.FAILED,
                        message=str(call.excinfo.value),
                        exception=call.excinfo.value
                    )

@pytest.fixture
def cop_verification_report():
    """
    Fixture for generating COP verification reports.
    
    Usage:
        def test_something(cop_verification_report):
            report = cop_verification_report(my_module)
            # Use the report
    """
    def _generate_report(module=None):
        return generate_verification_report(module)
    
    return _generate_report
