from typing import List, Optional, Dict, Any
from decimal import Decimal
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import sys
sys.path.append('/mnt/aux-data/teague/Projects/MindMeld/cop-testing/framework')
from cop_python.annotations import intent, invariant, risk, implementation_status, decision
from .user import User, Address
from .product import OrderItem


class OrderStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


@dataclass
class PaymentInfo:
    payment_method: str  # "credit_card", "paypal", "bank_transfer"
    payment_details: Dict[str, Any]
    billing_address: Address


@dataclass
class OrderRequest:
    user: User
    items: List[OrderItem]
    shipping_address: Address
    payment_info: PaymentInfo
    special_instructions: Optional[str] = None


@dataclass
class Order:
    order_id: str
    user: User
    items: List[OrderItem]
    shipping_address: Address
    payment_info: PaymentInfo
    status: OrderStatus = OrderStatus.PENDING
    subtotal: Decimal = field(default_factory=lambda: Decimal('0'))
    tax_amount: Decimal = field(default_factory=lambda: Decimal('0'))
    shipping_cost: Decimal = field(default_factory=lambda: Decimal('0'))
    total_amount: Decimal = field(default_factory=lambda: Decimal('0'))
    created_at: datetime = field(default_factory=datetime.now)
    special_instructions: Optional[str] = None

    @intent("Calculate subtotal from all order items")
    @invariant("subtotal >= 0")
    @implementation_status("IMPLEMENTED")
    def calculate_subtotal(self) -> Decimal:
        self.subtotal = sum(item.get_total_price() for item in self.items)
        return self.subtotal

    @intent("Calculate tax amount based on shipping address")
    @invariant("tax_amount >= 0 and tax_rate >= 0 and tax_rate <= 1")
    @decision("State-based tax calculation", alternatives=["ZIP-based", "Third-party service"])
    @implementation_status("IMPLEMENTED")
    def calculate_tax(self) -> Decimal:
        # Simplified tax calculation by state
        tax_rates = {
            'CA': Decimal('0.0825'),  # California
            'NY': Decimal('0.08'),    # New York
            'TX': Decimal('0.0625'),  # Texas
            'FL': Decimal('0.06'),    # Florida
        }
        
        tax_rate = tax_rates.get(self.shipping_address.state, Decimal('0.05'))  # Default 5%
        self.tax_amount = self.subtotal * tax_rate
        return self.tax_amount

    @intent("Calculate shipping costs for all items in order")
    @invariant("shipping_cost >= 0")
    @decision("Sum individual item shipping", alternatives=["Flat rate", "Weight-based total"])
    @implementation_status("IMPLEMENTED")
    def calculate_shipping(self) -> Decimal:
        self.shipping_cost = sum(
            item.product.calculate_shipping_cost(item.quantity, self.shipping_address.zip_code)
            for item in self.items
        )
        return self.shipping_cost

    @intent("Calculate final order total including tax and shipping")
    @invariant("total_amount > 0 and total_amount == subtotal + tax_amount + shipping_cost")
    @implementation_status("IMPLEMENTED")
    def calculate_total(self) -> Decimal:
        self.calculate_subtotal()
        self.calculate_tax()
        self.calculate_shipping()
        self.total_amount = self.subtotal + self.tax_amount + self.shipping_cost
        return self.total_amount

    @intent("Validate order meets all business requirements")
    @invariant("len(items) > 0 and total_amount > 0")
    @risk("MEDIUM", details="Invalid orders can cause payment and fulfillment issues")
    @implementation_status("IMPLEMENTED")
    def is_valid(self) -> bool:
        if not self.items:
            return False
            
        # Validate all items
        for item in self.items:
            if not item.is_valid():
                return False
                
        # Validate addresses
        if not self.shipping_address.is_valid():
            return False
            
        # Validate user can afford order
        self.calculate_total()
        if not self.user.can_afford(self.total_amount):
            return False
            
        return True

    @intent("Update order status with validation")
    @invariant("new_status in OrderStatus")
    @risk("LOW", details="Status transitions affect fulfillment workflow")
    @implementation_status("IMPLEMENTED")
    def update_status(self, new_status: OrderStatus) -> bool:
        # Validate status transitions
        valid_transitions = {
            OrderStatus.PENDING: [OrderStatus.PROCESSING, OrderStatus.CANCELLED],
            OrderStatus.PROCESSING: [OrderStatus.SHIPPED, OrderStatus.CANCELLED],
            OrderStatus.SHIPPED: [OrderStatus.DELIVERED],
            OrderStatus.DELIVERED: [OrderStatus.REFUNDED],
            OrderStatus.CANCELLED: [],  # Terminal state
            OrderStatus.REFUNDED: []    # Terminal state
        }
        
        if new_status not in valid_transitions.get(self.status, []):
            return False
            
        self.status = new_status
        return True


@dataclass
class OrderResult:
    success: bool
    order: Optional[Order] = None
    error_message: Optional[str] = None
    error_code: Optional[str] = None