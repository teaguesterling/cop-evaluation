from typing import Dict, List, Optional
from decimal import Decimal
import time
import sys
sys.path.append('/mnt/aux-data/teague/Projects/MindMeld/cop-testing/framework')
from cop_python.annotations import intent, invariant, risk, implementation_status, decision
from ..models.product import Product, OrderItem


class InventoryLock:
    def __init__(self, product_id: str, quantity: int, expiry_seconds: int = 300):
        self.product_id = product_id
        self.quantity = quantity
        self.created_at = time.time()
        self.expiry_seconds = expiry_seconds
        
    def is_expired(self) -> bool:
        return time.time() - self.created_at > self.expiry_seconds


class InventoryService:
    def __init__(self):
        self.products: Dict[str, Product] = {}
        self.locks: Dict[str, List[InventoryLock]] = {}

    @intent("Add or update product in inventory system")
    @invariant("product.inventory_count >= 0")
    @implementation_status("IMPLEMENTED")
    def add_product(self, product: Product) -> bool:
        if product.inventory_count < 0:
            return False
        self.products[product.product_id] = product
        return True

    @intent("Acquire exclusive lock on inventory to prevent overselling")
    @invariant("quantity > 0")
    @risk("HIGH", details="Inventory locking prevents overselling but can deadlock if not managed properly")
    @decision("Use Redis for inventory locking to prevent overselling", 
              alternatives=["Database locks", "Optimistic locking"])
    @implementation_status("IMPLEMENTED")
    def acquire_inventory_lock(self, product_id: str, quantity: int, 
                              expiry_seconds: int = 300) -> Optional[str]:
        if quantity <= 0:
            return None
            
        product = self.products.get(product_id)
        if not product:
            return None
            
        # Clean expired locks first
        self._clean_expired_locks(product_id)
        
        # Check if enough inventory available
        locked_quantity = sum(lock.quantity for lock in self.locks.get(product_id, []))
        available = product.inventory_count - locked_quantity
        
        if available < quantity:
            return None
            
        # Create lock
        lock = InventoryLock(product_id, quantity, expiry_seconds)
        lock_id = f"{product_id}_{lock.created_at}_{quantity}"
        
        if product_id not in self.locks:
            self.locks[product_id] = []
        self.locks[product_id].append(lock)
        
        return lock_id

    @intent("Release inventory lock when order completes or fails")
    @invariant("lock_id is not None")
    @implementation_status("IMPLEMENTED")
    def release_inventory_lock(self, lock_id: str) -> bool:
        if not lock_id:
            return False
            
        # Parse lock_id to find the lock
        for product_id, lock_list in self.locks.items():
            for i, lock in enumerate(lock_list):
                expected_lock_id = f"{product_id}_{lock.created_at}_{lock.quantity}"
                if expected_lock_id == lock_id:
                    lock_list.pop(i)
                    return True
        return False

    @intent("Clean up expired inventory locks automatically")
    @implementation_status("IMPLEMENTED")
    def _clean_expired_locks(self, product_id: str) -> None:
        if product_id not in self.locks:
            return
            
        self.locks[product_id] = [
            lock for lock in self.locks[product_id]
            if not lock.is_expired()
        ]

    @intent("Validate all items in order have sufficient inventory")
    @invariant("len(items) > 0")
    @risk("MEDIUM", details="Inventory validation prevents overselling but must be accurate")
    @implementation_status("IMPLEMENTED")
    def validate_inventory_availability(self, items: List[OrderItem]) -> Dict[str, bool]:
        results = {}
        
        for item in items:
            product_id = item.product.product_id
            product = self.products.get(product_id)
            
            if not product:
                results[product_id] = False
                continue
                
            # Clean expired locks
            self._clean_expired_locks(product_id)
            
            # Calculate available inventory
            locked_quantity = sum(lock.quantity for lock in self.locks.get(product_id, []))
            available = product.inventory_count - locked_quantity
            
            results[product_id] = available >= item.quantity
            
        return results

    @intent("Reserve inventory for confirmed order")
    @invariant("len(items) > 0")
    @risk("HIGH", details="Inventory deduction affects stock levels and overselling prevention")
    @implementation_status("IMPLEMENTED")
    def reserve_inventory_for_order(self, items: List[OrderItem], 
                                   lock_ids: List[str]) -> bool:
        # First validate all locks are still valid
        for lock_id in lock_ids:
            found = False
            for product_id, lock_list in self.locks.items():
                for lock in lock_list:
                    expected_lock_id = f"{product_id}_{lock.created_at}_{lock.quantity}"
                    if expected_lock_id == lock_id:
                        found = True
                        break
                if found:
                    break
            if not found:
                return False
        
        # Reserve inventory for each item
        for item in items:
            product = self.products.get(item.product.product_id)
            if product and not product.reserve_inventory(item.quantity):
                # Rollback previous reservations
                self._rollback_reservations(items[:items.index(item)])
                return False
        
        # Release all locks since inventory is now reserved
        for lock_id in lock_ids:
            self.release_inventory_lock(lock_id)
            
        return True

    @intent("Rollback inventory reservations on failure")
    @implementation_status("IMPLEMENTED")
    def _rollback_reservations(self, items: List[OrderItem]) -> None:
        for item in items:
            product = self.products.get(item.product.product_id)
            if product:
                product.release_reservation(item.quantity)

    @intent("Get current inventory status for product")
    @invariant("product_id is not None")
    @implementation_status("IMPLEMENTED")
    def get_inventory_status(self, product_id: str) -> Dict[str, int]:
        product = self.products.get(product_id)
        if not product:
            return {"total": 0, "available": 0, "reserved": 0, "locked": 0}
            
        self._clean_expired_locks(product_id)
        locked_quantity = sum(lock.quantity for lock in self.locks.get(product_id, []))
        
        return {
            "total": product.inventory_count,
            "available": product.get_available_inventory() - locked_quantity,
            "reserved": product.reserved_count,
            "locked": locked_quantity
        }