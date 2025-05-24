"""
Fraud detection and risk assessment module.
"""

from datetime import datetime, timedelta
from typing import Dict, List, Set
from dataclasses import dataclass
from decimal import Decimal

from cop_python.core import intent, invariant, risk, implementation_status, decision
from .payment_processor import PaymentRequest


@dataclass
class FraudAlert:
    """Fraud alert data structure."""
    alert_id: str
    transaction_id: str
    risk_level: str
    reasons: List[str]
    confidence: float
    timestamp: datetime


class FraudDetector:
    """Advanced fraud detection system with machine learning capabilities."""
    
    def __init__(self):
        self.transaction_history: Dict[str, List[PaymentRequest]] = {}
        self.blacklisted_customers: Set[str] = set()
        self.velocity_limits = {
            "per_minute": {"count": 5, "amount": Decimal("1000")},
            "per_hour": {"count": 20, "amount": Decimal("5000")},
            "per_day": {"count": 100, "amount": Decimal("25000")}
        }
    
    @intent("Detect fraudulent transactions using pattern analysis")
    @invariant("confidence >= 0.0 and confidence <= 1.0")
    @risk("CRITICAL", details="False positives block legitimate transactions, false negatives allow fraud")
    @implementation_status("PARTIAL", details="Rule-based detection implemented, ML models in development")
    @decision("AI", reasoning="ML models will enhance pattern detection beyond human-defined rules")
    def detect_fraud(self, request: PaymentRequest) -> FraudAlert:
        """
        Analyze transaction for fraud indicators using multiple detection methods.
        
        This is the main fraud detection entry point that combines multiple
        detection algorithms to assess transaction risk.
        """
        reasons = []
        risk_level = "LOW"
        confidence = 0.0
        
        # Check blacklist
        if self._is_blacklisted_customer(request.customer_id):
            reasons.append("Customer on blacklist")
            risk_level = "HIGH"
            confidence = max(confidence, 0.9)
        
        # Velocity checks
        velocity_risk = self._check_velocity_limits(request)
        if velocity_risk:
            reasons.extend(velocity_risk["reasons"])
            if velocity_risk["level"] == "HIGH":
                risk_level = "HIGH"
                confidence = max(confidence, 0.8)
            elif risk_level != "HIGH":
                risk_level = "MEDIUM"
                confidence = max(confidence, 0.6)
        
        # Amount anomaly detection
        amount_risk = self._detect_amount_anomaly(request)
        if amount_risk:
            reasons.extend(amount_risk["reasons"])
            if amount_risk["level"] == "HIGH" and risk_level != "HIGH":
                risk_level = "MEDIUM"
                confidence = max(confidence, 0.7)
        
        # Pattern analysis
        pattern_risk = self._analyze_transaction_patterns(request)
        if pattern_risk:
            reasons.extend(pattern_risk["reasons"])
            confidence = max(confidence, pattern_risk["confidence"])
        
        # Generate alert
        alert_id = f"fraud_{datetime.now().strftime('%Y%m%d%H%M%S')}_{request.customer_id}"
        
        return FraudAlert(
            alert_id=alert_id,
            transaction_id="",  # Will be set after transaction processing
            risk_level=risk_level,
            reasons=reasons if reasons else ["No fraud indicators detected"],
            confidence=confidence,
            timestamp=datetime.now()
        )
    
    @intent("Check if customer is on fraud blacklist")
    @invariant("customer_id is not None")
    @risk("HIGH", details="Blocking legitimate customers causes business loss")
    @implementation_status("IMPLEMENTED")
    def _is_blacklisted_customer(self, customer_id: str) -> bool:
        """Check if customer is on the fraud blacklist."""
        return customer_id in self.blacklisted_customers
    
    @intent("Detect velocity-based fraud patterns")
    @invariant("request is not None")
    @risk("HIGH", details="Velocity limits affect legitimate high-volume customers")
    @implementation_status("IMPLEMENTED")
    def _check_velocity_limits(self, request: PaymentRequest) -> Dict[str, any]:
        """Check if transaction violates velocity limits."""
        customer_history = self.transaction_history.get(request.customer_id, [])
        now = datetime.now()
        
        # Check different time windows
        for window, limits in self.velocity_limits.items():
            if window == "per_minute":
                cutoff = now - timedelta(minutes=1)
            elif window == "per_hour":
                cutoff = now - timedelta(hours=1)
            else:  # per_day
                cutoff = now - timedelta(days=1)
            
            recent_transactions = [
                t for t in customer_history 
                if hasattr(t, 'timestamp') and t.timestamp > cutoff
            ]
            
            transaction_count = len(recent_transactions)
            total_amount = sum(t.amount for t in recent_transactions)
            
            if (transaction_count >= limits["count"] or 
                total_amount >= limits["amount"]):
                return {
                    "level": "HIGH",
                    "reasons": [f"Velocity limit exceeded: {window}"],
                    "count": transaction_count,
                    "amount": total_amount
                }
        
        return None
    
    @intent("Detect anomalous transaction amounts for customer")
    @invariant("request is not None")
    @risk("MEDIUM", details="May flag legitimate large purchases")
    @implementation_status("PROTOTYPE", details="Basic statistical analysis implemented")
    def _detect_amount_anomaly(self, request: PaymentRequest) -> Dict[str, any]:
        """Detect if transaction amount is anomalous for this customer."""
        customer_history = self.transaction_history.get(request.customer_id, [])
        
        if len(customer_history) < 5:
            # Not enough history for analysis
            return None
        
        # Calculate customer's typical transaction amounts
        amounts = [float(t.amount) for t in customer_history[-20:]]  # Last 20 transactions
        avg_amount = sum(amounts) / len(amounts)
        max_amount = max(amounts)
        
        current_amount = float(request.amount)
        
        # Flag if significantly higher than typical
        if current_amount > avg_amount * 5 and current_amount > max_amount * 2:
            return {
                "level": "HIGH",
                "reasons": ["Transaction amount significantly exceeds customer pattern"],
                "current": current_amount,
                "average": avg_amount,
                "previous_max": max_amount
            }
        elif current_amount > avg_amount * 3:
            return {
                "level": "MEDIUM",
                "reasons": ["Transaction amount moderately exceeds customer pattern"],
                "current": current_amount,
                "average": avg_amount
            }
        
        return None
    
    @intent("Analyze transaction patterns for fraud indicators")
    @invariant("request is not None")
    @risk("MEDIUM", details="Pattern analysis may have false positives")
    @implementation_status("NOT_IMPLEMENTED", details="Advanced pattern analysis planned")
    @decision("AI", reasoning="Complex pattern detection requires ML algorithms")
    def _analyze_transaction_patterns(self, request: PaymentRequest) -> Dict[str, any]:
        """
        Analyze transaction patterns using advanced algorithms.
        
        This will use machine learning models to detect complex fraud patterns
        that are difficult to express as rules.
        """
        # Placeholder for advanced pattern analysis
        # Will be implemented with ML models
        return None
    
    @intent("Add customer to fraud blacklist")
    @risk("HIGH", details="Incorrectly blacklisting customers causes permanent business loss")
    @implementation_status("IMPLEMENTED")
    def blacklist_customer(self, customer_id: str, reason: str) -> None:
        """Add a customer to the fraud blacklist."""
        self.blacklisted_customers.add(customer_id)
    
    @intent("Remove customer from fraud blacklist")
    @risk("MEDIUM", details="Removing fraudulent customers from blacklist enables fraud")
    @implementation_status("IMPLEMENTED")
    def remove_from_blacklist(self, customer_id: str) -> None:
        """Remove a customer from the fraud blacklist."""
        self.blacklisted_customers.discard(customer_id)
    
    @intent("Record transaction for historical analysis")
    @implementation_status("IMPLEMENTED")
    @risk("LOW")
    def record_transaction(self, request: PaymentRequest) -> None:
        """Record transaction in customer history for pattern analysis."""
        if request.customer_id not in self.transaction_history:
            self.transaction_history[request.customer_id] = []
        
        # Add timestamp to request for velocity tracking
        request.timestamp = datetime.now()
        self.transaction_history[request.customer_id].append(request)
        
        # Keep only recent history (last 100 transactions per customer)
        if len(self.transaction_history[request.customer_id]) > 100:
            self.transaction_history[request.customer_id] = \
                self.transaction_history[request.customer_id][-100:]
    
    @intent("Get fraud detection statistics and metrics")
    @implementation_status("PARTIAL", details="Basic stats implemented")
    @risk("LOW")
    def get_fraud_stats(self) -> Dict[str, any]:
        """Get statistics about fraud detection performance."""
        total_customers = len(self.transaction_history)
        blacklisted_count = len(self.blacklisted_customers)
        
        return {
            "total_customers_tracked": total_customers,
            "blacklisted_customers": blacklisted_count,
            "velocity_limits": self.velocity_limits
        }