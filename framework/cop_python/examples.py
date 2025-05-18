"""
COP Framework Examples: Showcasing all features

This module provides comprehensive examples of using the COP framework
for AI agents to understand how to apply and interpret COP annotations.
"""

from cop_python.min import (
    intent, 
    implementation_status, 
    risk, 
    invariant, 
    decision,
    IMPLEMENTED, 
    PARTIAL, 
    NOT_IMPLEMENTED, 
    PLANNED,
    DEPRECATED,
    ConceptAnnotations,
    concept_annotations
)


# Example 1: Security-critical payment processing
@intent("Process user payments securely")
@implementation_status(PARTIAL, details="Only credit cards supported, no cryptocurrency")
@risk("Card data exposure", category="security", severity="HIGH", 
      impact="PCI compliance violation", 
      mitigation=["Data encrypted at rest", "TLS in transit"])
@invariant("Transactions must be atomic", critical=True)
@invariant("Card numbers must never be logged", critical=True)
@decision(brief="Use Stripe API", 
         rationale="Industry standard, handles compliance",
         implementor="human", 
         reason="Security-critical integration",
         decider="security_team",
         date="2023-04-15")
def process_payment(payment_data):
    """Process a payment through the payment gateway.
    
    Args:
        payment_data: Payment information including amount and card details
        
    Returns:
        Transaction result with ID and status
    """
    # Implementation would go here
    pass


# Example 2: Unimplemented feature with clear boundaries
@intent("Generate PDF financial reports")
@implementation_status(NOT_IMPLEMENTED)
@decision(implementor="ai", 
         constraints=[
             "Must follow company branding guidelines",
             "Include all required regulatory disclaimers",
             "Support A4 and Letter formats"
         ])
def generate_pdf_report(financial_data):
    """Generate a PDF report from financial data."""
    raise NotImplementedError("PDF generation not implemented yet")


# Example 3: Module-level annotations
# Using concept_annotations context manager for module-wide annotations
with concept_annotations:
    intent("Payment processing module for e-commerce platform")
    implementation_status(PARTIAL, details="Missing refund functionality")
    risk("PCI compliance required for entire module", category="security", severity="HIGH")
    decision("Microservices architecture", 
            rationale="Enables independent scaling of payment processing",
            decider="architecture_team")


# Example 4: Class with evolving implementation
@intent("Manage user shopping carts")
@implementation_status(IMPLEMENTED)
class ShoppingCart:
    """Shopping cart functionality for e-commerce."""
    
    @intent("Add items to cart with inventory checking")
    @implementation_status(IMPLEMENTED)
    @invariant("Cart total must be non-negative", critical=True)
    def add_item(self, item_id, quantity):
        """Add an item to the cart."""
        # Implementation
        pass
    
    @intent("Apply discount codes to cart")
    @implementation_status(PARTIAL, details="Only percentage discounts supported")
    @risk("Invalid discount codes could lead to revenue loss", severity="MEDIUM")
    def apply_discount(self, discount_code):
        """Apply a discount code to the cart."""
        # Implementation
        pass
    
    @intent("Calculate shipping costs based on location")
    @implementation_status(PLANNED)
    @decision(implementor="ai", 
             constraints=["Use postal code for zone calculation",
                         "Support international shipping zones"])
    def calculate_shipping(self, destination):
        """Calculate shipping cost to destination."""
        raise NotImplementedError("Shipping calculation planned for Q2")


# Example 5: Method with multiple annotations and context managers
def validate_and_process_order(order_data):
    """
    Validate and process an order through multiple stages.
    Shows how to use context managers for different code sections.
    """
    
    # Validation section - human implemented for security
    with decision(implementor="human", reason="Security-critical validation"):
        with risk("Input validation bypass", category="security", severity="HIGH"):
            # Validate order data
            if not order_data.get("items"):
                raise ValueError("Order must contain items")
            
            # Security checks
            if not validate_payment_method(order_data):
                raise ValueError("Invalid payment method")
    
    # Processing section - AI can implement
    with decision(implementor="ai", constraints=["Handle all error cases"]):
        with implementation_status(PARTIAL, details="No international support"):
            # Process the order
            result = process_order_internal(order_data)
    
    return result


# Example 6: Deprecated functionality
@intent("Legacy payment processing - do not use")
@implementation_status(DEPRECATED, alternative="Use process_payment() instead")
@risk("Uses outdated security protocols", severity="HIGH")
def process_payment_legacy(payment_info):
    """Deprecated: Use process_payment() instead."""
    import warnings
    warnings.warn("process_payment_legacy is deprecated", DeprecationWarning)
    # Legacy implementation
    pass


# Example 7: Buggy implementation needing fixes
@intent("Calculate tax based on jurisdiction")
@implementation_status(BUGGY, details="Incorrect calculation for interstate commerce")
@invariant("Tax rate must be between 0 and 1", critical=True)
@decision(implementor="human", 
         reason="Tax law expertise required",
         priority="high")
def calculate_tax(amount, jurisdiction):
    """Calculate tax for a given jurisdiction.
    
    Known issues:
    - Interstate commerce not handled correctly
    - Some jurisdictions return negative tax
    """
    # Buggy implementation that needs fixing
    pass


# Example 8: Using ConceptAnnotations for reusable annotation sets
payment_annotations = ConceptAnnotations([
    intent("Handle payment processing"),
    risk("PCI compliance required", category="security", severity="HIGH"),
    invariant("Payment amounts must be positive", critical=True)
])

# Apply the same annotations to multiple functions
@payment_annotations.apply_to
def process_credit_card(card_data):
    """Process credit card payment."""
    pass

@payment_annotations.apply_to
def process_debit_card(card_data):
    """Process debit card payment."""
    pass


# Example 9: Complex decision tracking
@intent("Select payment gateway provider")
@implementation_status(IMPLEMENTED)
@decision(brief="Selected Stripe over PayPal and Square",
         options=["Stripe", "PayPal", "Square", "Braintree"],
         answer="Stripe",
         rationale="Better API, lower fees for our volume",
         decider="CTO",
         date="2023-03-01",
         category="architecture",
         impact="high",
         ref="ARCH-2023-001")
class PaymentGatewaySelector:
    """Manages payment gateway selection and routing."""
    pass


# Example 10: Testing integration (when testing module is available)
# This shows how tests would be linked to components
# @invariant.test_for(process_payment, "Transactions must be atomic") 
# def test_payment_atomicity():
#     """Test that payment transactions are atomic."""
#     # Test implementation


def validate_payment_method(order_data):
    """Helper function for payment validation."""
    return True


def process_order_internal(order_data):
    """Internal order processing."""
    return {"status": "success", "order_id": "12345"}


# Main module exports
__all__ = [
    'process_payment',
    'generate_pdf_report', 
    'ShoppingCart',
    'validate_and_process_order',
    'process_payment_legacy',
    'calculate_tax',
    'process_credit_card',
    'process_debit_card',
    'PaymentGatewaySelector'
]