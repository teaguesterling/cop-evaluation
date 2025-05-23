"""Tests for cop_python.testing.assertions module."""

import unittest
from cop_python.runtime import enable_cop, disable_cop
from cop_python.testing.assertions import (
    # Invariant assertions
    assert_invariant,
    # Risk assertions
    assert_security_requirement,
    # Implementation status assertions
    assert_implemented,
    # Decision assertions
    assert_decision,
    # Intent assertions
    assert_intent,
    # Exception imports
    InvariantViolation,
    RiskViolation,
    ImplementationStatusMismatch,
    DecisionViolation,
    IntentViolation,
)
import cop_python.annotations as cop_annotations


class TestInvariantAssertions(unittest.TestCase):
    """Test invariant assertion functions."""
    
    def setUp(self):
        enable_cop()
    
    def tearDown(self):
        disable_cop()
    
    def test_assert_invariant_success(self):
        """Test successful invariant assertion."""
        # Should not raise when condition is True
        assert_invariant(True, "Test invariant")
        assert_invariant(1 + 1 == 2, "Math works")
    
    def test_assert_invariant_failure(self):
        """Test failed invariant assertion."""
        with self.assertRaises(InvariantViolation) as ctx:
            assert_invariant(False, "This should fail")
        self.assertIn("This should fail", str(ctx.exception))
    
    def test_assert_invariant_with_component(self):
        """Test invariant assertion with component."""
        def my_function():
            pass
        
        with self.assertRaises(InvariantViolation) as ctx:
            assert_invariant(False, "Component invariant", on=my_function)
        self.assertIn("my_function", str(ctx.exception))


class TestRiskAssertions(unittest.TestCase):
    """Test risk assertion functions."""
    
    def setUp(self):
        enable_cop()
    
    def tearDown(self):
        disable_cop()
    
    def test_assert_security_requirement_success(self):
        """Test successful security requirement assertion."""
        # Should not raise when condition is True
        assert_security_requirement(True, "Security check")
    
    def test_assert_security_requirement_failure(self):
        """Test failed security requirement assertion."""
        with self.assertRaises(RiskViolation) as ctx:
            assert_security_requirement(False, "Security breach")
        self.assertIn("Security breach", str(ctx.exception))
    
    def test_assert_security_requirement_with_component(self):
        """Test security requirement assertion with component."""
        def secure_function():
            pass
        
        with self.assertRaises(RiskViolation) as ctx:
            assert_security_requirement(False, "Access denied", on=secure_function)
        self.assertIn("secure_function", str(ctx.exception))


class TestImplementationAssertions(unittest.TestCase):
    """Test implementation status assertion functions."""
    
    def setUp(self):
        enable_cop()
    
    def tearDown(self):
        disable_cop()
    
    def test_assert_implemented_success(self):
        """Test successful implementation assertion."""
        assert_implemented(True, "Feature implemented")
    
    def test_assert_implemented_failure(self):
        """Test failed implementation assertion."""
        with self.assertRaises(ImplementationStatusMismatch) as ctx:
            assert_implemented(False, "Not implemented")
        self.assertIn("Not implemented", str(ctx.exception))
    
    def test_assert_implemented_with_component(self):
        """Test implementation assertion with component."""
        def new_feature():
            pass
        
        with self.assertRaises(ImplementationStatusMismatch) as ctx:
            assert_implemented(False, "Feature incomplete", on=new_feature)
        self.assertIn("new_feature", str(ctx.exception))


class TestDecisionAssertions(unittest.TestCase):
    """Test decision assertion functions."""
    
    def setUp(self):
        enable_cop()
    
    def tearDown(self):
        disable_cop()
    
    def test_assert_decision_success(self):
        """Test successful decision assertion."""
        assert_decision(True, "Design followed")
    
    def test_assert_decision_failure(self):
        """Test failed decision assertion."""
        with self.assertRaises(DecisionViolation) as ctx:
            assert_decision(False, "Design violated")
        self.assertIn("Design violated", str(ctx.exception))
    
    def test_assert_decision_with_component(self):
        """Test decision assertion with component."""
        def api_endpoint():
            pass
        
        with self.assertRaises(DecisionViolation) as ctx:
            assert_decision(False, "REST pattern not followed", on=api_endpoint)
        self.assertIn("api_endpoint", str(ctx.exception))


class TestIntentAssertions(unittest.TestCase):
    """Test intent assertion functions."""
    
    def setUp(self):
        enable_cop()
    
    def tearDown(self):
        disable_cop()
    
    def test_assert_intent_success(self):
        """Test successful intent assertion."""
        assert_intent(True, "Intent fulfilled")
    
    def test_assert_intent_failure(self):
        """Test failed intent assertion."""
        with self.assertRaises(IntentViolation) as ctx:
            assert_intent(False, "Intent not met")
        self.assertIn("Intent not met", str(ctx.exception))
    
    def test_assert_intent_with_component(self):
        """Test intent assertion with component."""
        def process_payment():
            pass
        
        with self.assertRaises(IntentViolation) as ctx:
            assert_intent(False, "Payment not processed", on=process_payment)
        self.assertIn("process_payment", str(ctx.exception))


class TestExceptionImports(unittest.TestCase):
    """Test that exceptions are properly imported."""
    
    def test_exception_imports(self):
        """Test all exception classes are available."""
        # Just verify we can create instances
        inv = InvariantViolation("test")
        risk = RiskViolation("test")
        impl = ImplementationStatusMismatch("test")
        dec = DecisionViolation("test")
        intent = IntentViolation("test")
        
        # Verify they're exceptions
        self.assertTrue(issubclass(InvariantViolation, Exception))
        self.assertTrue(issubclass(RiskViolation, Exception))
        self.assertTrue(issubclass(ImplementationStatusMismatch, Exception))
        self.assertTrue(issubclass(DecisionViolation, Exception))
        self.assertTrue(issubclass(IntentViolation, Exception))


class TestIntegration(unittest.TestCase):
    """Test integration with actual COP annotations."""
    
    def setUp(self):
        enable_cop()
    
    def tearDown(self):
        disable_cop()
    
    def test_invariant_integration(self):
        """Test assert_invariant with actual invariant annotations."""
        @cop_annotations.invariant("Must be positive")
        def positive_value(x):
            return x > 0
        
        # This should work fine
        assert_invariant(positive_value(5), "Must be positive", on=positive_value)
        
        # This should fail
        with self.assertRaises(InvariantViolation):
            assert_invariant(positive_value(-5), "Must be positive", on=positive_value)
    
    def test_risk_integration(self):
        """Test assert_security_requirement with risk annotations."""
        @cop_annotations.risk("SQL injection", severity="HIGH")
        def execute_query(query):
            return query
        
        # Test with clean input
        clean_query = "SELECT * FROM users WHERE id = ?"
        assert_security_requirement(
            "DROP" not in execute_query(clean_query),
            "No SQL injection",
            on=execute_query
        )
        
        # Test with malicious input
        bad_query = "SELECT * FROM users; DROP TABLE users"
        with self.assertRaises(RiskViolation):
            assert_security_requirement(
                "DROP" not in execute_query(bad_query),
                "SQL injection detected",
                on=execute_query
            )
    
    def test_implementation_integration(self):
        """Test assert_implemented with implementation_status annotations."""
        from cop_python.annotations import IMPLEMENTED, NOT_IMPLEMENTED
        
        @cop_annotations.implementation_status(IMPLEMENTED)
        def complete_feature():
            return True
        
        @cop_annotations.implementation_status(NOT_IMPLEMENTED)
        def incomplete_feature():
            raise NotImplementedError()
        
        # This should pass
        assert_implemented(
            hasattr(complete_feature, "__cop_annotations__"),
            "Feature is marked as implemented",
            on=complete_feature
        )
        
        # This should fail
        with self.assertRaises(ImplementationStatusMismatch):
            assert_implemented(
                False,  # We know it's not implemented
                "Feature should be implemented",
                on=incomplete_feature
            )
    
    def test_decision_integration(self):
        """Test assert_decision with decision annotations."""
        @cop_annotations.decision("Use REST API", implementor="architect")
        def api_design():
            return {"method": "GET", "path": "/users"}
        
        api_result = api_design()
        assert_decision(
            api_result["method"] in ["GET", "POST", "PUT", "DELETE"],
            "Uses REST verbs",
            on=api_design
        )
        
        # Test violation
        with self.assertRaises(DecisionViolation):
            assert_decision(
                api_result["method"] == "FETCH",  # Non-REST verb
                "Uses REST verbs",
                on=api_design
            )
    
    def test_intent_integration(self):
        """Test assert_intent with intent annotations."""
        @cop_annotations.intent("Process user payments securely")
        def process_payment(amount, card_number):
            # Simplified - in reality would handle encryption, etc.
            return {"status": "success", "amount": amount}
        
        result = process_payment(100, "1234-5678-9012-3456")
        assert_intent(
            result["status"] == "success",
            "Payment processed successfully",
            on=process_payment
        )
        
        # Test failure
        with self.assertRaises(IntentViolation):
            assert_intent(
                result["status"] == "failed",
                "Payment should fail",
                on=process_payment
            )


if __name__ == "__main__":
    unittest.main()