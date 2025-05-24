from typing import Optional, Dict, List
from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import sys
sys.path.append('/mnt/aux-data/teague/Projects/MindMeld/cop-testing/framework')
from cop_python.annotations import intent, invariant, risk, implementation_status, decision


class ProductCategory(Enum):
    ELECTRONICS = "electronics"
    CLOTHING = "clothing"
    BOOKS = "books"
    HOME_GARDEN = "home_garden"
    SPORTS = "sports"


@dataclass
class Product:
    product_id: str
    name: str
    description: str
    price: Decimal
    category: ProductCategory
    weight_oz: float
    dimensions_inches: Dict[str, float]  # length, width, height
    inventory_count: int
    reserved_count: int = 0
    is_active: bool = True
    created_at: datetime = None

    @intent("Calculate available inventory excluding reserved items")
    @invariant("available_inventory >= 0 and available_inventory <= inventory_count")
    @implementation_status("IMPLEMENTED")
    def get_available_inventory(self) -> int:
        return max(0, self.inventory_count - self.reserved_count)

    @intent("Check if sufficient inventory exists for requested quantity")
    @invariant("quantity > 0")
    @implementation_status("IMPLEMENTED")
    def has_sufficient_inventory(self, quantity: int) -> bool:
        if quantity <= 0:
            return False
        return self.get_available_inventory() >= quantity

    @intent("Reserve inventory for order processing")
    @invariant("quantity > 0 and quantity <= available_inventory")
    @risk("MEDIUM", details="Inventory reservations prevent overselling but can lock stock")
    @decision("Use reservation system", alternatives=["Optimistic locking", "Real-time deduction"])
    @implementation_status("IMPLEMENTED")
    def reserve_inventory(self, quantity: int) -> bool:
        if quantity <= 0 or not self.has_sufficient_inventory(quantity):
            return False
        self.reserved_count += quantity
        return True

    @intent("Release reserved inventory when order cancelled")
    @invariant("quantity > 0 and quantity <= reserved_count")
    @implementation_status("IMPLEMENTED")
    def release_reservation(self, quantity: int) -> bool:
        if quantity <= 0 or quantity > self.reserved_count:
            return False
        self.reserved_count -= quantity
        return True

    @intent("Calculate shipping cost based on weight and dimensions")
    @invariant("quantity > 0")
    @decision("Weight-based shipping calculation", alternatives=["Dimensional weight", "Flat rate"])
    @implementation_status("IMPLEMENTED") 
    def calculate_shipping_cost(self, quantity: int, destination_zip: str) -> Decimal:
        if quantity <= 0:
            return Decimal('0')
        
        total_weight = self.weight_oz * quantity
        base_cost = Decimal('5.99')  # Base shipping
        weight_cost = Decimal(str(total_weight * 0.1))  # $0.10 per oz
        
        # Premium shipping for far destinations (simplified)
        if destination_zip.startswith(('9', '0')):  # West coast, Hawaii
            weight_cost *= Decimal('1.5')
            
        return base_cost + weight_cost


@dataclass
class OrderItem:
    product: Product
    quantity: int
    unit_price: Decimal

    @intent("Calculate total price for this order item")
    @invariant("quantity > 0 and unit_price >= 0")
    @implementation_status("IMPLEMENTED")
    def get_total_price(self) -> Decimal:
        return self.unit_price * self.quantity

    @intent("Validate order item has valid quantity and pricing")
    @invariant("quantity > 0 and unit_price > 0")
    @risk("LOW", details="Invalid order items could lead to pricing errors")
    @implementation_status("IMPLEMENTED")
    def is_valid(self) -> bool:
        return (
            self.quantity > 0 and
            self.unit_price > 0 and
            self.product.is_active and
            self.product.has_sufficient_inventory(self.quantity)
        )