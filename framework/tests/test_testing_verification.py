"""Tests for cop_python.testing.verification module."""

import unittest
from unittest.mock import Mock, patch
import datetime
from cop_python.runtime import enable_cop, disable_cop, get_system
from cop_python.testing.verification import (
    VerificationResult,
    COPVerificationRecord,
    register_test_verification,
    record_verification_result,
    get_verification_results,
    clear_verification_registry,
    register_verification_failure,
    generate_verification_report,
    set_up_test_run,
    finish_test_run,
    _get_verification_registry,
)
from cop_python.utils import COPAnnotationReference
from cop_python.testing.foundation import COPTestData
from cop_python.core import COPNamespace
import cop_python.annotations as cop_annotations


class TestVerificationResult(unittest.TestCase):
    """Test the VerificationResult enum."""
    
    def test_verification_result_values(self):
        """Test that VerificationResult has expected values."""
        self.assertEqual(VerificationResult.PASSED.value, "PASSED")
        self.assertEqual(VerificationResult.FAILED.value, "FAILED")
        self.assertEqual(VerificationResult.SKIPPED.value, "SKIPPED")
        self.assertEqual(VerificationResult.ERROR.value, "ERROR")


class TestCOPVerificationRecord(unittest.TestCase):
    """Test the COPVerificationRecord class."""
    
    def test_record_creation(self):
        """Test creating a verification record."""
        annotation_ref = COPAnnotationReference(
            annotation_type="invariant",
            annotation_value="Must be positive",
            metadata_keys={"critical": True}
        )
        
        def test_func():
            pass
        
        record = COPVerificationRecord(
            test_id="test.module.test_func",
            annotation_reference=annotation_ref,
            component_id="module.function",
            component=test_func,
            result=VerificationResult.PASSED,
            timestamp="2024-01-01T12:00:00",
            message="Test passed"
        )
        
        self.assertEqual(record.test_id, "test.module.test_func")
        self.assertEqual(record.annotation_reference, annotation_ref)
        self.assertEqual(record.component_id, "module.function")
        self.assertEqual(record.component, test_func)
        self.assertEqual(record.result, VerificationResult.PASSED)
        self.assertEqual(record.timestamp, "2024-01-01T12:00:00")
        self.assertEqual(record.message, "Test passed")
    
    def test_record_to_dict(self):
        """Test converting a record to dictionary."""
        annotation_ref = COPAnnotationReference(
            annotation_type="risk",
            annotation_value="SQL injection",
            metadata_keys={"severity": "HIGH"}
        )
        
        def test_func():
            pass
        
        record = COPVerificationRecord(
            test_id="test.module.test_func",
            annotation_reference=annotation_ref,
            component_id="module.function",
            component=test_func,
            result=VerificationResult.FAILED,
            timestamp="2024-01-01T12:00:00",
            message="Test failed",
            exception=ValueError("Invalid input")
        )
        
        result = record.to_dict()
        
        self.assertEqual(result["test_id"], "test.module.test_func")
        self.assertEqual(result["annotation_reference"]["annotation_type"], "risk")
        self.assertEqual(result["annotation_reference"]["annotation_value"], "SQL injection")
        self.assertEqual(result["annotation_reference"]["metadata_keys"], {"severity": "HIGH"})
        self.assertEqual(result["component_id"], "module.function")
        self.assertEqual(result["result"], "FAILED")
        self.assertEqual(result["timestamp"], "2024-01-01T12:00:00")
        self.assertEqual(result["message"], "Test failed")
        self.assertIn("Invalid input", result["exception"])


class TestVerificationRegistry(unittest.TestCase):
    """Test the verification registry functions."""
    
    def setUp(self):
        enable_cop()
        clear_verification_registry()
    
    def tearDown(self):
        clear_verification_registry()
        disable_cop()
    
    def test_get_verification_registry(self):
        """Test getting the verification registry."""
        registry = _get_verification_registry()
        self.assertIsInstance(registry, dict)
        
        # Should get the same registry on subsequent calls (content-wise)
        registry["test"] = "value"
        registry2 = _get_verification_registry()
        self.assertEqual(registry2["test"], "value")
    
    def test_clear_verification_registry(self):
        """Test clearing the verification registry."""
        # Add something to the registry
        registry = _get_verification_registry()
        registry["test_data"] = "test"
        
        # Clear it
        clear_verification_registry()
        
        # Get the new registry
        new_registry = _get_verification_registry()
        
        # Should be a new, empty registry
        self.assertIsNot(registry, new_registry)
        self.assertNotIn("test_data", new_registry)
    
    def test_register_test_verification(self):
        """Test registering a test verification."""
        def test_func():
            pass
        
        def component_func():
            pass
        
        annotation_ref = COPAnnotationReference(
            annotation_type="invariant",
            annotation_value="Must be valid",
            metadata_keys={}
        )
        
        test_data = COPTestData(
            test_id="test.module.test_func",
            annotation_reference=annotation_ref,
            test_metadata={},
            source_info=None
        )
        
        record = register_test_verification(
            test_func, 
            component_func, 
            annotation_ref,
            test_data
        )
        
        self.assertEqual(record.annotation_reference, annotation_ref)
        self.assertEqual(record.component, component_func)
        self.assertEqual(record.test_data, test_data)
        
        # Check that it's stored in the registry
        registry = _get_verification_registry()
        self.assertIn("invariant", registry)
        self.assertIn(record.component_id, registry["invariant"])
        self.assertIn(record, registry["invariant"][record.component_id])
    
    def test_record_verification_result(self):
        """Test recording a verification result."""
        def test_func():
            pass
        
        def component_func():
            pass
        
        annotation_ref = COPAnnotationReference(
            annotation_type="risk",
            annotation_value="Security risk",
            metadata_keys={"severity": "HIGH"}
        )
        
        # First register the test
        register_test_verification(test_func, component_func, annotation_ref)
        
        # Then record the result
        with patch('cop_python.testing.verification.datetime') as mock_datetime:
            mock_datetime.datetime.now.return_value.isoformat.return_value = "2024-01-01T12:00:00"
            
            record = record_verification_result(
                test_func,
                component_func,
                annotation_ref,
                VerificationResult.PASSED,
                message="Test passed successfully"
            )
        
        self.assertEqual(record.result, VerificationResult.PASSED)
        self.assertEqual(record.message, "Test passed successfully")
        self.assertEqual(record.timestamp, "2024-01-01T12:00:00")
    
    def test_get_verification_results(self):
        """Test getting verification results."""
        def test_func1():
            pass
        
        def test_func2():
            pass
        
        def component1():
            pass
        
        def component2():
            pass
        
        # Register some verifications
        annotation_ref1 = COPAnnotationReference("invariant", "Must be positive", {})
        annotation_ref2 = COPAnnotationReference("risk", "Security risk", {})
        
        register_test_verification(test_func1, component1, annotation_ref1)
        register_test_verification(test_func2, component2, annotation_ref2)
        
        # Get all results
        all_results = get_verification_results()
        self.assertEqual(len(all_results), 2)
        
        # Get results for specific component
        comp1_results = get_verification_results(component=component1)
        self.assertEqual(len(comp1_results), 1)
        self.assertEqual(comp1_results[0].component, component1)
        
        # Get results for specific annotation type
        invariant_results = get_verification_results(annotation_type="invariant")
        self.assertEqual(len(invariant_results), 1)
        self.assertEqual(invariant_results[0].annotation_reference.annotation_type, "invariant")
    
    def test_register_verification_failure(self):
        """Test register_verification_failure (currently a placeholder)."""
        # This function is currently a placeholder, so just test it doesn't raise
        register_verification_failure(
            component=lambda: None,
            annotation_type="invariant",
            annotation_args=("Must be valid",),
            failure_type="AssertionError",
            failure_reason="Invariant violated"
        )


class TestVerificationReport(unittest.TestCase):
    """Test the verification report generation."""
    
    def setUp(self):
        enable_cop()
        clear_verification_registry()
    
    def tearDown(self):
        clear_verification_registry()
        disable_cop()
    
    def test_generate_empty_report(self):
        """Test generating a report with no verifications."""
        report = generate_verification_report()
        
        self.assertIn("summary", report)
        self.assertIn("details", report)
        self.assertEqual(report["summary"]["components_checked"], 0)
        self.assertEqual(report["summary"]["annotations_total"], 0)
    
    def test_generate_report_with_module(self):
        """Test generating a report for a specific module."""
        # Create a mock module with some components
        module = type('module', (), {})()
        
        @cop_annotations.invariant("Must be positive")
        def func1(x):
            return x > 0
        
        @cop_annotations.risk("Security risk", severity="HIGH")
        def func2():
            pass
        
        # Add functions to module
        module.func1 = func1
        module.func2 = func2
        
        # Register some verifications
        annotation_ref1 = COPAnnotationReference("invariant", "Must be positive", {})
        annotation_ref2 = COPAnnotationReference("risk", "Security risk", {"severity": "HIGH"})
        
        register_test_verification(lambda: None, func1, annotation_ref1)
        register_test_verification(lambda: None, func2, annotation_ref2)
        
        # Record some results
        record_verification_result(
            lambda: None, 
            func1, 
            annotation_ref1, 
            VerificationResult.PASSED
        )
        record_verification_result(
            lambda: None, 
            func2, 
            annotation_ref2, 
            VerificationResult.FAILED
        )
        
        # Generate report
        report = generate_verification_report(module)
        
        self.assertEqual(report["summary"]["components_checked"], 2)
        self.assertEqual(report["summary"]["annotations_total"], 2)
        self.assertEqual(report["summary"]["annotations_verified"], 1)
        self.assertEqual(report["summary"]["annotations_failed"], 1)
    
    def test_test_run_lifecycle(self):
        """Test the test run lifecycle functions."""
        # Set up test run
        set_up_test_run()
        
        # Verify registry is clear
        registry = _get_verification_registry()
        # Check that registry is empty
        self.assertEqual(len(registry), 0, f"Registry should be empty but contains: {registry}")
        
        # Add some test data
        annotation_ref = COPAnnotationReference("invariant", "Test", {})
        register_test_verification(lambda: None, lambda: None, annotation_ref)
        
        # Finish test run and get report
        report = finish_test_run()
        
        self.assertIn("summary", report)
        self.assertIn("details", report)


class TestIntegration(unittest.TestCase):
    """Test integration with the testing framework."""
    
    def setUp(self):
        enable_cop()
        clear_verification_registry()
    
    def tearDown(self):
        clear_verification_registry()
        disable_cop()
    
    def test_full_verification_flow(self):
        """Test the full verification flow from registration to report."""
        # Create test components with annotations
        @cop_annotations.invariant("Must be non-empty")
        @cop_annotations.risk("Input validation", severity="MEDIUM")
        def validate_input(data):
            return bool(data)
        
        @cop_annotations.implementation_status(cop_annotations.IMPLEMENTED)
        def process_data(data):
            return data.upper()
        
        # Create test functions
        def test_validate_input():
            assert validate_input("test")
        
        def test_process_data():
            assert process_data("test") == "TEST"
        
        # Register verifications
        inv_ref = COPAnnotationReference("invariant", "Must be non-empty", {})
        risk_ref = COPAnnotationReference("risk", "Input validation", {"severity": "MEDIUM"})
        impl_ref = COPAnnotationReference("implementation_status", cop_annotations.IMPLEMENTED, {})
        
        register_test_verification(test_validate_input, validate_input, inv_ref)
        register_test_verification(test_validate_input, validate_input, risk_ref)
        register_test_verification(test_process_data, process_data, impl_ref)
        
        # Record results
        record_verification_result(
            test_validate_input, 
            validate_input, 
            inv_ref, 
            VerificationResult.PASSED
        )
        record_verification_result(
            test_validate_input, 
            validate_input, 
            risk_ref, 
            VerificationResult.PASSED
        )
        record_verification_result(
            test_process_data, 
            process_data, 
            impl_ref, 
            VerificationResult.FAILED,
            message="Implementation incomplete"
        )
        
        # Get results
        all_results = get_verification_results()
        self.assertEqual(len(all_results), 3)
        
        # Generate report
        report = generate_verification_report()
        self.assertEqual(report["summary"]["annotations_verified"], 2)
        self.assertEqual(report["summary"]["annotations_failed"], 1)


if __name__ == "__main__":
    unittest.main()