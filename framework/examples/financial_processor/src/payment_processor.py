"""
Payment processing module with comprehensive COP annotations.
"""

from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime

from cop_python.core import intent, invariant, risk, implementation_status, decision


class PaymentMethod(Enum):
    """Supported payment methods."""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    DIGITAL_WALLET = "digital_wallet"
    CRYPTOCURRENCY = "cryptocurrency"


@dataclass
class PaymentRequest:
    """Payment request data structure."""
    amount: Decimal
    currency: str
    payment_method: PaymentMethod
    merchant_id: str
    customer_id: str
    description: str
    metadata: Dict[str, str] = None


@dataclass
class PaymentResult:
    """Payment processing result."""
    transaction_id: str
    status: str
    amount: Decimal
    fees: Decimal
    processing_time_ms: int
    risk_score: float


class PaymentProcessor:
    """Core payment processing engine with comprehensive COP annotations."""
    
    def __init__(self, max_transaction_limit: Decimal = Decimal('10000.00')):
        self.max_transaction_limit = max_transaction_limit
        self.processed_count = 0
    
    @intent("Process secure payment transactions with fraud detection")
    @invariant("amount > 0 and amount <= max_transaction_limit")
    @risk("HIGH", details="Handles sensitive financial data and payment credentials")
    @implementation_status("IMPLEMENTED")
    def process_payment(self, request: PaymentRequest) -> PaymentResult:
        """
        Process a payment transaction with comprehensive validation.
        
        This is the core payment processing method that handles
        all payment types with fraud detection and validation.
        """
        # Validate amount
        if request.amount <= 0:
            raise ValueError("Payment amount must be positive")
        
        if request.amount > self.max_transaction_limit:
            raise ValueError(f"Amount exceeds limit of {self.max_transaction_limit}")
        
        # Simulate payment processing
        start_time = datetime.now()
        
        # Calculate fees based on payment method
        fees = self._calculate_fees(request.amount, request.payment_method)
        
        # Generate transaction ID
        self.processed_count += 1
        transaction_id = f"txn_{request.merchant_id}_{self.processed_count}"
        
        # Calculate risk score
        risk_score = self._calculate_risk_score(request)
        
        processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
        
        return PaymentResult(
            transaction_id=transaction_id,
            status="completed",
            amount=request.amount,
            fees=fees,
            processing_time_ms=processing_time,
            risk_score=risk_score
        )
    
    @intent("Calculate transaction fees based on payment method and amount")
    @invariant("amount > 0")
    @risk("MEDIUM", details="Fee calculation affects revenue")
    @implementation_status("IMPLEMENTED")
    def _calculate_fees(self, amount: Decimal, payment_method: PaymentMethod) -> Decimal:
        """Calculate processing fees for a transaction."""
        fee_rates = {
            PaymentMethod.CREDIT_CARD: Decimal('0.029'),  # 2.9%
            PaymentMethod.DEBIT_CARD: Decimal('0.015'),   # 1.5%
            PaymentMethod.BANK_TRANSFER: Decimal('0.005'), # 0.5%
            PaymentMethod.DIGITAL_WALLET: Decimal('0.025'), # 2.5%
            PaymentMethod.CRYPTOCURRENCY: Decimal('0.01'),  # 1.0%
        }
        
        base_fee = amount * fee_rates.get(payment_method, Decimal('0.03'))
        
        # Minimum fee of $0.30
        return max(base_fee, Decimal('0.30'))
    
    @intent("Assess transaction risk for fraud prevention")
    @invariant("risk_score >= 0.0 and risk_score <= 1.0")
    @risk("HIGH", details="Critical for fraud prevention and compliance")
    @implementation_status("PARTIAL", details="Basic rules implemented, ML model planned")
    @decision("AI", reasoning="Risk scoring will use ML models for pattern detection")
    def _calculate_risk_score(self, request: PaymentRequest) -> float:
        """
        Calculate risk score for transaction (0.0 = low risk, 1.0 = high risk).
        
        Currently uses basic rules, will be enhanced with ML models.
        """
        risk_score = 0.0
        
        # Amount-based risk
        if request.amount > Decimal('1000'):
            risk_score += 0.2
        if request.amount > Decimal('5000'):
            risk_score += 0.3
        
        # Payment method risk
        method_risk = {
            PaymentMethod.CREDIT_CARD: 0.1,
            PaymentMethod.DEBIT_CARD: 0.05,
            PaymentMethod.BANK_TRANSFER: 0.02,
            PaymentMethod.DIGITAL_WALLET: 0.15,
            PaymentMethod.CRYPTOCURRENCY: 0.4,
        }
        
        risk_score += method_risk.get(request.payment_method, 0.2)
        
        # Currency risk (non-USD adds risk)
        if request.currency != "USD":
            risk_score += 0.1
        
        return min(risk_score, 1.0)
    
    @intent("Validate payment request data before processing")
    @invariant("request is not None")
    @risk("MEDIUM", details="Invalid data could cause processing errors")
    @implementation_status("IMPLEMENTED")
    def validate_payment_request(self, request: PaymentRequest) -> bool:
        """Validate payment request data integrity."""
        if not request:
            return False
        
        if not request.amount or request.amount <= 0:
            return False
        
        if not request.currency or len(request.currency) != 3:
            return False
        
        if not request.merchant_id or not request.customer_id:
            return False
        
        if request.payment_method not in PaymentMethod:
            return False
        
        return True
    
    @intent("Check if payment method is supported")
    @implementation_status("PARTIAL", details="Limited payment methods supported")
    @risk("LOW")
    def is_payment_method_supported(self, method: PaymentMethod) -> bool:
        """Check if a payment method is currently supported."""
        supported_methods = {
            PaymentMethod.CREDIT_CARD,
            PaymentMethod.DEBIT_CARD,
            PaymentMethod.BANK_TRANSFER,
            PaymentMethod.DIGITAL_WALLET,
        }
        
        return method in supported_methods
    
    @intent("Get current transaction processing statistics")
    @implementation_status("IMPLEMENTED")
    @risk("LOW")
    def get_processing_stats(self) -> Dict[str, int]:
        """Get statistics about processed transactions."""
        return {
            "total_processed": self.processed_count,
            "max_transaction_limit": float(self.max_transaction_limit)
        }