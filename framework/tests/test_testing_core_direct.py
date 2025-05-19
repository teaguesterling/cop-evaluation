"""Direct tests for cop_python.testing.core module without using __init__.py."""

import sys
import unittest

# Import the core module directly to bypass __init__.py 
sys.path.insert(0, '/mnt/aux-data/teague/Projects/MindMeld/cop-testing/framework')
from cop_python.testing import core as testing_core
from cop_python.runtime import enable_cop, disable_cop, get_system, SourceInfo
from cop_python.utils import COPAnnotationReference


class TestExceptionClasses(unittest.TestCase):
    """Test custom exception classes."""
    
    def test_exception_hierarchy(self):
        """Test that all exceptions inherit from COPAnnotationViolation."""
        self.assertTrue(issubclass(testing_core.InvariantViolation, testing_core.COPAnnotationViolation))
        self.assertTrue(issubclass(testing_core.RiskViolation, testing_core.COPAnnotationViolation))
        self.assertTrue(issubclass(testing_core.ImplementationStatusMismatch, testing_core.COPAnnotationViolation))
        self.assertTrue(issubclass(testing_core.DecisionViolation, testing_core.COPAnnotationViolation))
        self.assertTrue(issubclass(testing_core.IntentViolation, testing_core.COPAnnotationViolation))
        
    def test_cop_annotation_violation_is_assertion_error(self):
        """Test that COPAnnotationViolation is an AssertionError."""
        self.assertTrue(issubclass(testing_core.COPAnnotationViolation, AssertionError))
        
    def test_exception_instantiation(self):
        """Test that exceptions can be instantiated with messages."""
        exc = testing_core.InvariantViolation("Test invariant violation")
        self.assertEqual(str(exc), "Test invariant violation")
        
        exc = testing_core.RiskViolation("Security breach")
        self.assertEqual(str(exc), "Security breach")


class TestCOPTestData(unittest.TestCase):
    """Test the COPTestData structure."""
    
    def setUp(self):
        enable_cop()
        
    def tearDown(self):
        disable_cop()
    
    def test_cop_test_data_creation(self):
        """Test creating a COPTestData instance."""
        annotation_ref = COPAnnotationReference(
            annotation_type="invariant",
            annotation_value="Must be positive",
            metadata_keys={"critical": True}
        )
        
        test_data = testing_core.COPTestData(
            test_id="test_module.test_function",
            annotation_reference=annotation_ref,
            test_metadata={"priority": "high"},
            source_info=None
        )
        
        self.assertEqual(test_data.test_id, "test_module.test_function")
        self.assertEqual(test_data.annotation_reference, annotation_ref)
        self.assertEqual(test_data.test_metadata, {"priority": "high"})
        self.assertIsNone(test_data.source_info)
        
    def test_cop_test_data_to_dict(self):
        """Test converting COPTestData to dictionary."""
        annotation_ref = COPAnnotationReference(
            annotation_type="risk",
            annotation_value="Security risk",
            metadata_keys={"severity": "HIGH"}
        )
        
        test_data = testing_core.COPTestData(
            test_id="test_module.TestClass.test_method",
            annotation_reference=annotation_ref,
            test_metadata={"category": "security"},
            source_info=None
        )
        
        result = test_data.to_dict()
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result["test_id"], "test_module.TestClass.test_method")
        self.assertIn("annotation_reference", result)
        self.assertEqual(result["test_metadata"], {"category": "security"})


if __name__ == "__main__":
    # Remove cop_python.testing from sys.modules to force fresh import
    if 'cop_python.testing' in sys.modules:
        del sys.modules['cop_python.testing']
    
    unittest.main()