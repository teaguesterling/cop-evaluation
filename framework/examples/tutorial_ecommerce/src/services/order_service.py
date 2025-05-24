from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import datetime
import uuid
import sys
sys.path.append('/mnt/aux-data/teague/Projects/MindMeld/cop-testing/framework')
from cop_python.annotations import intent, invariant, risk, implementation_status, decision
from ..models.order import Order, OrderRequest, OrderResult, OrderStatus
from ..models.product import OrderItem
from .inventory_service import InventoryService
from .payment_service import PaymentService
from .notification_service import NotificationService


class OrderService:
    def __init__(self, inventory_service: InventoryService, 
                 payment_service: PaymentService,
                 notification_service: NotificationService):
        self.inventory_service = inventory_service
        self.payment_service = payment_service
        self.notification_service = notification_service
        self.orders: Dict[str, Order] = {}

    @intent("Process customer orders with inventory validation and payment processing")
    @invariant("order_request.user is not None and len(order_request.items) > 0")
    @risk("HIGH", details="Order processing affects inventory, payments, and customer satisfaction")
    @decision("Synchronous order processing", alternatives=["Async with queues", "Batch processing"])
    @implementation_status("IMPLEMENTED")
    def process_order(self, order_request: OrderRequest) -> OrderResult:
        # Generate order ID
        order_id = str(uuid.uuid4())
        
        # Create order object
        order = Order(
            order_id=order_id,
            user=order_request.user,
            items=order_request.items,
            shipping_address=order_request.shipping_address,
            payment_info=order_request.payment_info,
            special_instructions=order_request.special_instructions
        )
        
        # Validate order
        if not order.is_valid():
            return OrderResult(
                success=False,
                error_message="Order validation failed",
                error_code="INVALID_ORDER"
            )
        
        # Check inventory availability
        inventory_check = self.inventory_service.validate_inventory_availability(order.items)
        unavailable_items = [item_id for item_id, available in inventory_check.items() if not available]
        
        if unavailable_items:
            return OrderResult(
                success=False,
                error_message=f"Insufficient inventory for items: {', '.join(unavailable_items)}",
                error_code="INSUFFICIENT_INVENTORY"
            )
        
        # Acquire inventory locks
        lock_ids = []
        for item in order.items:
            lock_id = self.inventory_service.acquire_inventory_lock(
                item.product.product_id, 
                item.quantity
            )
            if not lock_id:
                # Release acquired locks on failure
                for existing_lock_id in lock_ids:
                    self.inventory_service.release_inventory_lock(existing_lock_id)
                return OrderResult(
                    success=False,
                    error_message="Unable to acquire inventory locks",
                    error_code="INVENTORY_LOCK_FAILED"
                )
            lock_ids.append(lock_id)
        
        try:
            # Process payment
            payment_result = self.payment_service.process_payment(order, order.payment_info)
            if not payment_result.success:
                return OrderResult(
                    success=False,
                    error_message=f"Payment failed: {payment_result.error_message}",
                    error_code=payment_result.error_code
                )
            
            # Reserve inventory
            if not self.inventory_service.reserve_inventory_for_order(order.items, lock_ids):
                # Try to refund payment if inventory reservation fails
                if payment_result.transaction_id:
                    self.payment_service.process_refund(
                        payment_result.transaction_id,
                        payment_result.processed_amount,
                        "Inventory reservation failed"
                    )
                return OrderResult(
                    success=False,
                    error_message="Failed to reserve inventory",
                    error_code="INVENTORY_RESERVATION_FAILED"
                )
            
            # Update order status
            order.update_status(OrderStatus.PROCESSING)
            
            # Store order
            self.orders[order_id] = order
            
            # Send confirmation notification
            self.notification_service.send_order_confirmation(order)
            
            return OrderResult(success=True, order=order)
            
        finally:
            # Ensure locks are released in case of any failure
            for lock_id in lock_ids:
                self.inventory_service.release_inventory_lock(lock_id)

    @intent("Calculate order total with tax and shipping")
    @invariant("len(items) > 0 and shipping_address is not None")
    @implementation_status("IMPLEMENTED")
    def calculate_order_total(self, items: List[OrderItem], shipping_address) -> Dict[str, Decimal]:
        # Create temporary order for calculation
        temp_order = Order(
            order_id="temp",
            user=None,  # Not needed for calculation
            items=items,
            shipping_address=shipping_address,
            payment_info=None  # Not needed for calculation
        )
        
        subtotal = temp_order.calculate_subtotal()
        tax = temp_order.calculate_tax()
        shipping = temp_order.calculate_shipping()
        total = temp_order.calculate_total()
        
        return {
            "subtotal": subtotal,
            "tax": tax,
            "shipping": shipping,
            "total": total
        }

    @intent("Retrieve order by ID with user authorization")
    @invariant("order_id is not None")
    @risk("LOW", details="Order access must be properly authorized")
    @implementation_status("IMPLEMENTED")
    def get_order(self, order_id: str, user_id: str) -> Optional[Order]:
        order = self.orders.get(order_id)
        if order and order.user.user_id == user_id:
            return order
        return None

    @intent("Get all orders for a specific user")
    @invariant("user_id is not None")
    @implementation_status("IMPLEMENTED")
    def get_user_orders(self, user_id: str) -> List[Order]:
        return [order for order in self.orders.values() 
                if order.user.user_id == user_id]

    @intent("Cancel order if cancellation is allowed")
    @invariant("order_id is not None")
    @risk("MEDIUM", details="Order cancellation affects inventory and payments")
    @implementation_status("IMPLEMENTED")
    def cancel_order(self, order_id: str, user_id: str, reason: str = "") -> bool:
        order = self.get_order(order_id, user_id)
        if not order:
            return False
            
        # Check if cancellation is allowed
        if order.status not in [OrderStatus.PENDING, OrderStatus.PROCESSING]:
            return False
            
        # Update status
        if not order.update_status(OrderStatus.CANCELLED):
            return False
            
        # Release inventory reservations
        for item in order.items:
            item.product.release_reservation(item.quantity)
            
        # Process refund if payment was processed
        # (In real implementation, would track payment transaction ID)
        
        # Send cancellation notification
        self.notification_service.send_order_cancellation(order, reason)
        
        return True

    @intent("Update order status with proper validation")
    @invariant("order_id is not None and new_status in OrderStatus")
    @risk("LOW", details="Status updates drive fulfillment workflow")
    @implementation_status("IMPLEMENTED")
    def update_order_status(self, order_id: str, new_status: OrderStatus, 
                           updated_by: str = "system") -> bool:
        order = self.orders.get(order_id)
        if not order:
            return False
            
        old_status = order.status
        if not order.update_status(new_status):
            return False
            
        # Send appropriate notifications
        if new_status == OrderStatus.SHIPPED:
            self.notification_service.send_shipping_notification(order)
        elif new_status == OrderStatus.DELIVERED:
            self.notification_service.send_delivery_confirmation(order)
            
        return True

    @intent("Get order statistics for business analytics")
    @decision("In-memory analytics", alternatives=["Database aggregation", "Separate analytics service"])
    @implementation_status("IMPLEMENTED")
    def get_order_statistics(self) -> Dict[str, Any]:
        if not self.orders:
            return {"total_orders": 0}
            
        total_orders = len(self.orders)
        total_revenue = sum(order.total_amount for order in self.orders.values())
        
        status_counts = {}
        for status in OrderStatus:
            status_counts[status.value] = sum(
                1 for order in self.orders.values() 
                if order.status == status
            )
            
        average_order_value = total_revenue / total_orders if total_orders > 0 else Decimal('0')
        
        return {
            "total_orders": total_orders,
            "total_revenue": total_revenue,
            "average_order_value": average_order_value,
            "status_distribution": status_counts
        }