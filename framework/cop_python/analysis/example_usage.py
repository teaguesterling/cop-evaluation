#!/usr/bin/env python3
"""
Example usage of the COP static analysis toolkit with test relationship extraction.

This example demonstrates the complete workflow from code annotation to 
test relationship tracking and verification status analysis.
"""

from cop_python.core import intent, invariant, risk, implementation_status


# Example 1: Annotated code with COP annotations
class PaymentProcessor:
    """Example payment processing class with COP annotations."""
    
    @intent("Process secure payment transactions")
    @invariant("amount > 0 and amount <= max_transaction_limit")
    @risk("HIGH", details="Handles sensitive financial data")
    @implementation_status("IMPLEMENTED")
    def process_payment(self, amount: float, payment_method: str) -> dict:
        """Process a payment transaction."""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        # Simulate payment processing
        return {
            "status": "success",
            "transaction_id": f"txn_{amount}_{payment_method}",
            "amount": amount
        }
    
    @intent("Validate payment method is supported")
    @implementation_status("PARTIAL", details="Only supports credit cards")
    @risk("MEDIUM")
    def validate_payment_method(self, method: str) -> bool:
        """Validate if payment method is supported."""
        supported_methods = ["credit_card", "debit_card"]
        return method in supported_methods


# Example 2: Test file with relationship decorators
def test_for(component, **kwargs):
    """Mock test_for decorator for demonstration."""
    def decorator(func):
        return func
    return decorator

def test_invariant(component, invariant_value):
    """Mock test_invariant decorator for demonstration."""
    def decorator(func):
        return func
    return decorator

def test_risk(component, risk_value):
    """Mock test_risk decorator for demonstration."""
    def decorator(func):
        return func
    return decorator


# Test functions with relationship decorators
@test_for("PaymentProcessor.process_payment")
def test_process_payment_basic():
    """Test basic payment processing functionality."""
    processor = PaymentProcessor()
    result = processor.process_payment(100.0, "credit_card")
    assert result["status"] == "success"
    assert result["amount"] == 100.0


@test_invariant("PaymentProcessor.process_payment", "amount > 0")
def test_process_payment_positive_amount():
    """Test that payment processing enforces positive amounts."""
    processor = PaymentProcessor()
    try:
        processor.process_payment(-10.0, "credit_card")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected


@test_risk("PaymentProcessor.process_payment", "HIGH")
def test_process_payment_security():
    """Test high-risk security scenarios for payment processing."""
    processor = PaymentProcessor()
    # Test with potentially malicious input
    result = processor.process_payment(1000000.0, "credit_card")
    assert "transaction_id" in result


@test_for("PaymentProcessor.validate_payment_method", test_type="integration")
def test_validate_payment_method_integration():
    """Integration test for payment method validation."""
    processor = PaymentProcessor()
    assert processor.validate_payment_method("credit_card") is True
    assert processor.validate_payment_method("bitcoin") is False


def main():
    """Demonstrate the complete static analysis workflow."""
    import tempfile
    import os
    from pathlib import Path
    
    # Create temporary files with our example code
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Write the annotated code to a file
        code_file = temp_path / "payment_processor.py"
        with open(__file__, 'r') as f:
            source = f.read()
        
        # Extract just the PaymentProcessor class
        lines = source.split('\n')
        start_idx = next(i for i, line in enumerate(lines) if "class PaymentProcessor:" in line)
        end_idx = next(i for i, line in enumerate(lines[start_idx:], start_idx) 
                      if line and not line.startswith(' ') and not line.startswith('\t') 
                      and "class PaymentProcessor:" not in line)
        
        class_code = '\n'.join([
            "from cop_python.core import intent, invariant, risk, implementation_status",
            ""
        ] + lines[start_idx:end_idx])
        
        code_file.write_text(class_code)
        
        # Write the test code to a file
        test_file = temp_path / "test_payment_processor.py"
        test_start = next(i for i, line in enumerate(lines) if "def test_for(" in line)
        test_code = '\n'.join(lines[test_start:])
        test_file.write_text(test_code)
        
        print("=== COP Static Analysis Toolkit Demo ===\n")
        
        # Demonstrate CLI usage
        print("1. Extract COP annotations:")
        print(f"   python -m cop_python.analysis.cli extract {code_file}")
        print()
        
        print("2. Extract test relationships:")
        print(f"   python -m cop_python.analysis.cli test-extract {test_file}")
        print()
        
        print("3. Build complete concept graph:")
        print(f"   python -m cop_python.analysis.cli test-build {code_file} --test-path {test_file}")
        print()
        
        print("4. Export for graph database analysis:")
        print(f"   python -m cop_python.analysis.cli export {code_file} --output-dir graph_data/")
        print()
        
        # Demonstrate Python API usage
        print("=== Python API Demo ===\n")
        
        from cop_python.analysis.extractor import extract_annotations_from_file
        from cop_python.analysis.test_extractor import extract_test_relationships_from_file
        from cop_python.analysis.graph import ConceptGraph
        
        # Extract annotations
        annotations = extract_annotations_from_file(str(code_file))
        print(f"Found {len(annotations)} annotations:")
        for anno in annotations:
            print(f"  - {anno.component_name}: {anno.annotation_type} = {anno.value}")
        print()
        
        # Extract test relationships
        test_relationships = extract_test_relationships_from_file(str(test_file))
        print(f"Found {len(test_relationships)} test relationships:")
        for rel in test_relationships:
            print(f"  - {rel.test_name} -> {rel.target_component}")
            if rel.annotation_ref:
                print(f"    Tests {rel.annotation_ref['type']}: {rel.annotation_ref['value']}")
        print()
        
        # Build concept graph
        graph = ConceptGraph()
        graph.build_from_annotations(annotations)
        graph.build_from_test_relationships(test_relationships)
        
        # Show verification status
        print("Verification Status:")
        for component_name in ["PaymentProcessor.process_payment", "PaymentProcessor.validate_payment_method"]:
            component_id = f"component:{component_name}"
            status = graph.get_verification_status(component_id)
            print(f"  - {component_name}:")
            print(f"    Total tests: {status['total_tests']}")
            print(f"    Test types: {status['test_types']}")
            print(f"    Annotation coverage: {status['annotation_coverage']}")
        
        print(f"\nGraph Summary:")
        print(f"  - Components: {len([n for n in graph.nodes.values() if n.node_type.value == 'component'])}")
        print(f"  - Annotations: {len([n for n in graph.nodes.values() if n.node_type.value == 'annotation'])}")
        print(f"  - Tests: {len([n for n in graph.nodes.values() if n.node_type.value == 'test'])}")
        print(f"  - Relationships: {len(graph.edges)}")


if __name__ == "__main__":
    main()