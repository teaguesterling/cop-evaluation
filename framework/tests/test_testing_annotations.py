"""Tests for cop_python.testing.annotations module."""

import unittest
from cop_python.runtime import enable_cop, disable_cop, get_system
from cop_python.testing.foundation import (
    COPAnnotationViolation,
    InvariantViolation,
    RiskViolation,
    ImplementationStatusMismatch,
    DecisionViolation,
    IntentViolation,
)
from cop_python.testing.annotations import (
    COPAnnotationTestingMixin,
    intent,
    implementation_status,
    risk,
    invariant,
    decision,
    COPTestingIntent,
    COPTestingImplementationStatus,
    COPTestingRisk,
    COPTestingInvariant,
    COPTestingDecision,
)
from cop_python.annotations import IMPLEMENTED, PARTIAL, NOT_IMPLEMENTED, Intent, ImplementationStatus, Risk, Invariant, Decision
from cop_python.utils import COPAnnotationReference
import cop_python.core as cop_core
import cop_python.annotations as cop_annotations


class TestCOPAnnotationTestingMixin(unittest.TestCase):
    """Test the COPAnnotationTestingMixin functionality."""
    
    def setUp(self):
        enable_cop()
        
    def tearDown(self):
        disable_cop()
    
    def test_exception_cls_attribute(self):
        """Test that mixin has exception_cls attribute."""
        mixin = COPAnnotationTestingMixin()
        self.assertEqual(mixin.exception_cls, COPAnnotationViolation)
    
    def test_test_for_decorator(self):
        """Test the test_for class method decorator."""
        # Create a test component
        def test_component():
            """Test component function."""
            pass
        
        # Create a test function using test_for
        @invariant.test_for(test_component, "Must be positive", critical=True)
        def test_positive_invariant():
            """Test that the invariant holds."""
            return True
        
        # Check that test was registered on component
        self.assertTrue(hasattr(test_component, "__cop_tests__"))
        self.assertIn("invariant", test_component.__cop_tests__.__dict__)
        
        # Check test metadata
        invariant_tests = test_component.__cop_tests__.invariant
        self.assertEqual(len(invariant_tests), 1)
        test_data = invariant_tests[0]
        self.assertEqual(test_data.annotation_reference.annotation_type, "invariant")
        self.assertEqual(test_data.annotation_reference.annotation_value, "Must be positive")
        self.assertEqual(test_data.annotation_reference.metadata_keys, {"critical": True})
        
        # Test function should be linked to component
        self.assertTrue(hasattr(test_positive_invariant, "__cop_tests__"))
        self.assertIn("invariant", test_positive_invariant.__cop_tests__.__dict__)
        self.assertEqual(test_positive_invariant.__cop_tests__.invariant[0], test_component)
    
    def test_assertion_method(self):
        """Test the assertion class method."""
        # Test successful assertion
        try:
            invariant.assertion(True, "This should pass")
        except Exception as e:
            self.fail(f"Assertion should not have raised: {e}")
        
        # Test failed assertion
        with self.assertRaises(InvariantViolation) as ctx:
            invariant.assertion(False, "This should fail")
        self.assertEqual(str(ctx.exception), "This should fail")
        
        # Test with component context
        def my_component():
            pass
        
        with self.assertRaises(InvariantViolation) as ctx:
            invariant.assertion(False, "Failed invariant", on=my_component)
        self.assertIn("Failed invariant", str(ctx.exception))
        self.assertIn("my_component", str(ctx.exception))
    
    def test_test_suite_decorator(self):
        """Test the test_suite decorator for test classes."""
        @invariant.test_suite("Must be valid", critical=True)
        class TestValidation(unittest.TestCase):
            def test_something(self):
                pass
        
        # Check class attributes
        self.assertEqual(TestValidation.__cop_annotation_type__, "invariant")
        self.assertEqual(TestValidation.__cop_annotation_args__, ("Must be valid",))
        self.assertEqual(TestValidation.__cop_annotation_kwargs__, {"critical": True})
        
        # setUp should have been modified
        instance = TestValidation()
        self.assertTrue(hasattr(instance, 'setUp'))
        
        # Call setUp to test context setting
        instance.setUp()
        self.assertEqual(instance.annotation_type, "invariant")
        self.assertEqual(instance.annotation_args, ("Must be valid",))
    
    def test_verify_context_manager(self):
        """Test the verify method context manager."""
        # Test basic verification context
        with invariant.verify("Test invariant") as ctx:
            # Should be able to specify component
            ctx.for_component(lambda: None)
            self.assertIsNotNone(ctx.component)
        
        # Test with exception inside context
        try:
            with invariant.verify("Test invariant") as ctx:
                raise AssertionError("Test failure")
        except AssertionError:
            pass  # Expected
        
        # Context should exit cleanly
        self.assertTrue(True)


class TestEnhancedAnnotations(unittest.TestCase):
    """Test the enhanced annotation classes."""
    
    def setUp(self):
        enable_cop()
        
    def tearDown(self):
        disable_cop()
    
    def test_intent_enhanced(self):
        """Test enhanced intent annotation."""
        # Should be a subclass with testing capabilities
        self.assertTrue(hasattr(intent, 'test_for'))
        self.assertTrue(hasattr(intent, 'assertion'))
        self.assertTrue(hasattr(intent, 'test_suite'))
        self.assertTrue(hasattr(intent, 'verify'))
        
        # Test creating an intent
        @intent("Process payments")
        def process_payment():
            pass
        
        # Check annotation was applied
        self.assertTrue(hasattr(process_payment, "__cop_annotations__"))
        intent_anno = process_payment.__cop_annotations__.intent[0]
        self.assertEqual(intent_anno.value, "Process payments")
    
    def test_implementation_status_enhanced(self):
        """Test enhanced implementation_status annotation."""
        @implementation_status(IMPLEMENTED)
        def implemented_function():
            pass
        
        # Check annotation
        self.assertTrue(hasattr(implemented_function, "__cop_annotations__"))
        status_anno = implemented_function.__cop_annotations__.implementation_status[0]
        self.assertEqual(status_anno.value, IMPLEMENTED)
        
        # Test assertion
        with self.assertRaises(ImplementationStatusMismatch):
            implementation_status.assertion(False, "Not implemented", on=implemented_function)
    
    def test_risk_enhanced(self):
        """Test enhanced risk annotation."""
        @risk("Security risk", severity="HIGH", category="security")
        def risky_function():
            pass
        
        # Check annotation
        self.assertTrue(hasattr(risky_function, "__cop_annotations__"))
        risk_anno = risky_function.__cop_annotations__.risk[0]
        self.assertEqual(risk_anno.value, "Security risk")
        self.assertEqual(risk_anno.metadata["severity"], "HIGH")
        
        # Test assertion
        with self.assertRaises(RiskViolation):
            risk.assertion(False, "Security breach")
    
    def test_invariant_enhanced(self):
        """Test enhanced invariant annotation."""
        @invariant("Must be positive", critical=True)
        def positive_only(x):
            return x > 0
        
        # Check annotation
        self.assertTrue(hasattr(positive_only, "__cop_annotations__"))
        inv_anno = positive_only.__cop_annotations__.invariant[0]
        self.assertEqual(inv_anno.value, "Must be positive")
        self.assertTrue(inv_anno.metadata["critical"])
        
        # Test assertion
        with self.assertRaises(InvariantViolation):
            invariant.assertion(False, "Invariant violated")
    
    def test_decision_enhanced(self):
        """Test enhanced decision annotation."""
        @decision("Use third-party API", implementor="human", rationale="Industry standard")
        def api_integration():
            pass
        
        # Check annotation
        self.assertTrue(hasattr(api_integration, "__cop_annotations__"))
        dec_anno = api_integration.__cop_annotations__.decision[0]
        self.assertEqual(dec_anno.value, "Use third-party API")
        self.assertEqual(dec_anno.metadata["implementor"], "human")
        
        # Test assertion
        with self.assertRaises(DecisionViolation):
            decision.assertion(False, "Decision not followed")


class TestTestingClasses(unittest.TestCase):
    """Test the testing-enhanced annotation classes."""
    
    def setUp(self):
        enable_cop()
        
    def tearDown(self):
        disable_cop()
    
    def test_creates_subclass(self):
        """Test that function creates a proper subclass."""
        # Since we changed to direct inheritance, test our actual classes
        TestingClass = COPTestingInvariant
        
        # Should have all the testing methods
        self.assertTrue(hasattr(TestingClass, 'test_for'))
        self.assertTrue(hasattr(TestingClass, 'assertion'))
        self.assertTrue(hasattr(TestingClass, 'test_suite'))
        self.assertTrue(hasattr(TestingClass, 'verify'))
        
        # Should be a subclass of the core annotation
        self.assertTrue(issubclass(TestingClass, cop_annotations.Invariant))
        self.assertTrue(issubclass(TestingClass, COPAnnotationTestingMixin))
    
    def test_subclass_exception_handling(self):
        """Test that subclass uses correct exception."""
        # Test that each testing class uses its specific exception
        with self.assertRaises(InvariantViolation):
            COPTestingInvariant.assertion(False, "Invariant failure")
            
        with self.assertRaises(IntentViolation):
            COPTestingIntent.assertion(False, "Intent failure")
            
        with self.assertRaises(RiskViolation):
            COPTestingRisk.assertion(False, "Risk failure")


class TestIntegrationWithCore(unittest.TestCase):
    """Test integration between testing and core annotations."""
    
    def setUp(self):
        enable_cop()
        
    def tearDown(self):
        disable_cop()
    
    def test_test_for_integration(self):
        """Test that test_for properly integrates with core components."""
        # Create a component with core annotations
        @cop_annotations.intent("Calculate total")
        @cop_annotations.implementation_status(IMPLEMENTED)
        def calculate_total(items):
            return sum(item.price for item in items)
        
        # Create tests for the component
        @intent.test_for(calculate_total, "Calculate total")
        def test_intent_fulfilled():
            # Mock test
            return True
        
        @invariant.test_for(calculate_total, "Result must be non-negative")
        def test_non_negative():
            # Mock test
            return True
        
        # Verify test registration
        self.assertTrue(hasattr(calculate_total, "__cop_tests__"))
        self.assertIn("intent", calculate_total.__cop_tests__.__dict__)
        self.assertIn("invariant", calculate_total.__cop_tests__.__dict__)
        
        # Verify test linking
        self.assertEqual(test_intent_fulfilled.__cop_tests__.intent[0], calculate_total)
        self.assertEqual(test_non_negative.__cop_tests__.invariant[0], calculate_total)
    
    def test_assertion_with_core_components(self):
        """Test assertions work with core-annotated components."""
        @cop_annotations.risk("Data exposure", severity="HIGH")
        def unsafe_operation():
            pass
        
        # Test assertion with component
        with self.assertRaises(RiskViolation) as ctx:
            risk.assertion(False, "Security check failed", on=unsafe_operation)
        
        self.assertIn("Security check failed", str(ctx.exception))
        self.assertIn("unsafe_operation", str(ctx.exception))
    
    def test_context_manager_with_core(self):
        """Test verify context manager with core components."""
        @cop_annotations.invariant("Must validate input")
        def process_input(data):
            if not data:
                raise ValueError("Invalid input")
            return data
        
        # Test verification context
        with invariant.verify("Must validate input") as ctx:
            ctx.for_component(process_input)
            # Simulate test within context
            try:
                process_input(None)
            except ValueError:
                pass  # Expected
        
        # Context should have handled the component
        self.assertEqual(ctx.component, process_input)


if __name__ == "__main__":
    unittest.main()