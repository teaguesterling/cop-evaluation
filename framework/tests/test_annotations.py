# tests/test_annotations.py
import unittest
from cop_python.runtime import enable_cop, disable_cop
from cop_python.annotations import (
    intent, implementation_status, risk, invariant, decision,
    IMPLEMENTED, PARTIAL, PLANNED, NOT_IMPLEMENTED, BUGGY, DEPRECATED, UNKNOWN
)

class TestIntentAnnotation(unittest.TestCase):
    """Test the intent annotation."""
    
    def setUp(self):
        enable_cop()
        
    def tearDown(self):
        disable_cop()
        
    def test_intent_creation(self):
        """Test creating an intent annotation."""
        # Create an intent annotation
        annotation = intent("Process user payment")
        
        # Check properties
        self.assertEqual(annotation.value, "Process user payment")
        self.assertEqual(annotation.kind, "intent")
        
    def test_intent_application(self):
        """Test applying an intent annotation to an object."""
        # Create a test function
        def test_function(): pass
        
        # Apply intent
        result = intent("Process user payment")(test_function)
        
        # Result should be the function
        self.assertIs(result, test_function)
        
        # Function should have the intent annotation
        self.assertTrue(hasattr(test_function, "__cop_annotations__"))
        annotations = test_function.__cop_annotations__.intent
        self.assertEqual(len(annotations), 1)
        self.assertEqual(annotations[0].value, "Process user payment")

class TestImplementationStatusAnnotation(unittest.TestCase):
    """Test the implementation_status annotation."""
    
    def setUp(self):
        enable_cop()
        
    def tearDown(self):
        disable_cop()
        
    def test_implementation_status_creation(self):
        """Test creating an implementation_status annotation."""
        # Create an implementation_status annotation
        annotation = implementation_status(IMPLEMENTED)
        
        # Check properties
        self.assertEqual(annotation.value, IMPLEMENTED)
        self.assertEqual(annotation.kind, "implementation_status")
        
    def test_implementation_status_with_details(self):
        """Test implementation_status with details."""
        # Create with details
        annotation = implementation_status(PARTIAL, details="Only supports credit cards")
        
        # Check properties
        self.assertEqual(annotation.value, PARTIAL)
        self.assertEqual(annotation.metadata.get("details"), "Only supports credit cards")
        
    def test_implementation_status_with_alternative(self):
        """Test implementation_status with alternative."""
        # Create with alternative
        annotation = implementation_status(DEPRECATED, alternative="use new_function instead")
        
        # Check properties
        self.assertEqual(annotation.value, DEPRECATED)
        self.assertEqual(annotation.metadata.get("alternative"), "use new_function instead")

class TestRiskAnnotation(unittest.TestCase):
    """Test the risk annotation."""
    
    def setUp(self):
        enable_cop()
        
    def tearDown(self):
        disable_cop()
        
    def test_risk_creation(self):
        """Test creating a risk annotation."""
        # Create a risk annotation
        annotation = risk("SQL injection vulnerability")
        
        # Check properties
        self.assertEqual(annotation.value, "SQL injection vulnerability")
        self.assertEqual(annotation.kind, "risk")
        
        # Default values
        self.assertEqual(annotation.metadata.get("category"), "security")
        self.assertEqual(annotation.metadata.get("severity"), "MEDIUM")
        
    def test_risk_with_custom_values(self):
        """Test risk with custom values."""
        # Create with custom values
        annotation = risk(
            "Performance degradation with large datasets",
            category="performance",
            severity="HIGH",
            impact="System becomes unresponsive",
            mitigation=["Pagination", "Caching"]
        )
        
        # Check properties
        self.assertEqual(annotation.value, "Performance degradation with large datasets")
        self.assertEqual(annotation.metadata.get("category"), "performance")
        self.assertEqual(annotation.metadata.get("severity"), "HIGH")
        self.assertEqual(annotation.metadata.get("impact"), "System becomes unresponsive")
        self.assertEqual(annotation.metadata.get("mitigation"), ["Pagination", "Caching"])

class TestInvariantAnnotation(unittest.TestCase):
    """Test the invariant annotation."""
    
    def setUp(self):
        enable_cop()
        
    def tearDown(self):
        disable_cop()
        
    def test_invariant_creation(self):
        """Test creating an invariant annotation."""
        # Create an invariant annotation
        annotation = invariant("Transaction amount must be positive")
        
        # Check properties
        self.assertEqual(annotation.value, "Transaction amount must be positive")
        self.assertEqual(annotation.kind, "invariant")
        
        # Default values
        self.assertEqual(annotation.metadata.get("critical"), False)
        
    def test_critical_invariant(self):
        """Test critical invariant."""
        # Create a critical invariant
        annotation = invariant("Passwords must be encrypted", critical=True)
        
        # Check properties
        self.assertEqual(annotation.value, "Passwords must be encrypted")
        self.assertEqual(annotation.metadata.get("critical"), True)

class TestDecisionAnnotation(unittest.TestCase):
    """Test the decision annotation."""
    
    def setUp(self):
        enable_cop()
        
    def tearDown(self):
        disable_cop()
        
    def test_decision_creation(self):
        """Test creating a decision annotation."""
        # Create a decision annotation
        annotation = decision("Use microservices architecture")
        
        # Check properties
        self.assertEqual(annotation.value, "Use microservices architecture")
        self.assertEqual(annotation.kind, "decision")
        
    def test_implementation_guidance(self):
        """Test implementation guidance."""
        # Create implementation guidance
        annotation = decision(
            implementor="human",
            reason="Requires domain expertise"
        )
        
        # Check properties
        self.assertEqual(annotation.value, "implementation boundary")  # Default value
        self.assertEqual(annotation.metadata.get("implementor"), "human")
        self.assertEqual(annotation.metadata.get("reason"), "Requires domain expertise")
        
    def test_architectural_decision(self):
        """Test architectural decision."""
        # Create architectural decision
        annotation = decision(
            "Use microservices architecture",
            rationale="Better scalability and team autonomy",
            options=["Monolith", "Microservices", "Serverless"],
            decider="architecture_team",
            category="architecture"
        )
        
        # Check properties
        self.assertEqual(annotation.value, "Use microservices architecture")
        self.assertEqual(annotation.metadata.get("rationale"), "Better scalability and team autonomy")
        self.assertEqual(annotation.metadata.get("options"), ["Monolith", "Microservices", "Serverless"])
        self.assertEqual(annotation.metadata.get("decider"), "architecture_team")
        self.assertEqual(annotation.metadata.get("category"), "architecture")

if __name__ == "__main__":
    unittest.main()
