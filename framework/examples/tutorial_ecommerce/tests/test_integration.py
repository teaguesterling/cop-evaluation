import unittest
from decimal import Decimal
from datetime import datetime
import sys
sys.path.append('/mnt/aux-data/teague/Projects/MindMeld/cop-testing/framework')
from cop_python.testing.annotations import test_for, test_invariant, test_risk

# Import all components for integration testing
sys.path.append('/mnt/aux-data/teague/Projects/MindMeld/cop-testing/framework/examples/tutorial_ecommerce')
from src.models.user import User, Address
from src.models.product import Product, ProductCategory, OrderItem
from src.models.order import Order, OrderStatus, OrderRequest, PaymentInfo
from src.services.inventory_service import InventoryService
from src.services.payment_service import PaymentService
from src.services.notification_service import NotificationService
from src.services.order_service import OrderService


class TestECommerceIntegration(unittest.TestCase):
    """Integration tests that verify the complete e-commerce workflow"""
    
    def setUp(self):
        # Set up all services
        self.inventory_service = InventoryService()
        self.payment_service = PaymentService()
        self.notification_service = NotificationService()
        self.order_service = OrderService(
            self.inventory_service,
            self.payment_service,
            self.notification_service
        )
        
        # Set up test data
        self.address = Address(
            street="123 Main Street",
            city="Anytown",
            state="CA",
            zip_code="12345"
        )
        
        self.user = User(
            user_id="user123",
            email="john.doe@example.com",
            first_name="John",
            last_name="Doe",
            credit_limit=Decimal('1000.00'),
            current_balance=Decimal('0.00'),
            addresses=[self.address],
            created_at=datetime.now(),
            is_premium=True
        )
        
        # Create multiple products
        self.products = [
            Product(
                product_id="laptop001",
                name="Gaming Laptop",
                description="High-performance gaming laptop",
                price=Decimal('899.99'),
                category=ProductCategory.ELECTRONICS,
                weight_oz=80.0,
                dimensions_inches={"length": 15, "width": 10, "height": 1},
                inventory_count=50
            ),
            Product(
                product_id="mouse001",
                name="Wireless Mouse",
                description="Ergonomic wireless mouse",
                price=Decimal('29.99'),
                category=ProductCategory.ELECTRONICS,
                weight_oz=4.0,
                dimensions_inches={"length": 4, "width": 2, "height": 1},
                inventory_count=200
            ),
            Product(
                product_id="book001",
                name="Programming Guide",
                description="Complete programming guide",
                price=Decimal('49.99'),
                category=ProductCategory.BOOKS,
                weight_oz=16.0,
                dimensions_inches={"length": 9, "width": 6, "height": 1},
                inventory_count=75
            )
        ]
        
        # Add products to inventory
        for product in self.products:
            self.inventory_service.add_product(product)
        
        # Create order items
        self.order_items = [
            OrderItem(product=self.products[0], quantity=1, unit_price=self.products[0].price),
            OrderItem(product=self.products[1], quantity=2, unit_price=self.products[1].price),
            OrderItem(product=self.products[2], quantity=1, unit_price=self.products[2].price)
        ]
        
        self.payment_info = PaymentInfo(
            payment_method="credit_card",
            payment_details={
                "card_number": "4111111111111111",
                "cvv": "123",
                "expiry_month": 12,
                "expiry_year": 2025
            },
            billing_address=self.address
        )

    @test_for("Complete e-commerce order workflow")
    @test_risk("HIGH", component="Complete order processing workflow")
    def test_complete_order_workflow(self):
        """Test the complete workflow from order creation to completion"""
        
        # Step 1: Create order request
        order_request = OrderRequest(
            user=self.user,
            items=self.order_items,
            shipping_address=self.address,
            payment_info=self.payment_info
        )
        
        # Step 2: Process the order
        result = self.order_service.process_order(order_request)
        
        # Verify order was created successfully
        self.assertTrue(result.success, f"Order processing failed: {result.error_message}")
        self.assertIsNotNone(result.order)
        self.assertEqual(result.order.status, OrderStatus.PROCESSING)
        
        order = result.order
        
        # Step 3: Verify inventory was reserved
        for item in self.order_items:
            product = self.inventory_service.products[item.product.product_id]
            self.assertEqual(product.reserved_count, item.quantity)
        
        # Step 4: Verify payment was processed
        self.assertEqual(len(self.payment_service.transactions), 1)
        
        # Step 5: Verify notification was sent
        self.assertEqual(len(self.notification_service.messages), 1)
        confirmation_msg = self.notification_service.messages[0]
        self.assertEqual(confirmation_msg.notification_type, "order_confirmation")
        self.assertEqual(confirmation_msg.recipient, self.user.email)
        
        # Step 6: Update order status to shipped
        ship_result = self.order_service.update_order_status(order.order_id, OrderStatus.SHIPPED)
        self.assertTrue(ship_result)
        
        # Verify shipping notification was sent
        self.assertEqual(len(self.notification_service.messages), 2)
        shipping_msg = self.notification_service.messages[1]
        self.assertEqual(shipping_msg.notification_type, "shipping_notification")
        
        # Step 7: Update order status to delivered
        delivery_result = self.order_service.update_order_status(order.order_id, OrderStatus.DELIVERED)
        self.assertTrue(delivery_result)
        
        # Verify delivery notification was sent
        self.assertEqual(len(self.notification_service.messages), 3)
        delivery_msg = self.notification_service.messages[2]
        self.assertEqual(delivery_msg.notification_type, "delivery_confirmation")

    @test_for("Order cancellation workflow")
    @test_risk("MEDIUM", component="Order cancellation and inventory release")
    def test_order_cancellation_workflow(self):
        """Test order cancellation and proper cleanup"""
        
        # Create and process an order
        order_request = OrderRequest(
            user=self.user,
            items=self.order_items[:1],  # Just one item for simplicity
            shipping_address=self.address,
            payment_info=self.payment_info
        )
        
        result = self.order_service.process_order(order_request)
        self.assertTrue(result.success)
        
        order = result.order
        product = self.products[0]
        
        # Verify inventory was reserved
        initial_reserved = product.reserved_count
        self.assertEqual(initial_reserved, 1)
        
        # Cancel the order
        cancel_result = self.order_service.cancel_order(
            order.order_id, 
            self.user.user_id, 
            "Customer changed mind"
        )
        self.assertTrue(cancel_result)
        
        # Verify order status was updated
        cancelled_order = self.order_service.get_order(order.order_id, self.user.user_id)
        self.assertEqual(cancelled_order.status, OrderStatus.CANCELLED)
        
        # Verify inventory reservation was released
        self.assertEqual(product.reserved_count, initial_reserved - 1)
        
        # Verify cancellation notification was sent
        cancellation_msgs = [
            msg for msg in self.notification_service.messages 
            if msg.notification_type == "order_cancellation"
        ]
        self.assertEqual(len(cancellation_msgs), 1)

    @test_for("Inventory insufficient stock handling")
    @test_invariant("Inventory constraints are enforced")
    @test_risk("MEDIUM", component="Inventory validation and error handling")
    def test_insufficient_inventory_handling(self):
        """Test proper handling when insufficient inventory is available"""
        
        # Create order for more items than available
        large_order_item = OrderItem(
            product=self.products[0], 
            quantity=100,  # More than the 50 available
            unit_price=self.products[0].price
        )
        
        order_request = OrderRequest(
            user=self.user,
            items=[large_order_item],
            shipping_address=self.address,
            payment_info=self.payment_info
        )
        
        # Attempt to process the order
        result = self.order_service.process_order(order_request)
        
        # Verify order failed due to insufficient inventory
        self.assertFalse(result.success)
        self.assertEqual(result.error_code, "INSUFFICIENT_INVENTORY")
        
        # Verify no inventory was reserved
        product = self.inventory_service.products[self.products[0].product_id]
        self.assertEqual(product.reserved_count, 0)
        
        # Verify no payment was processed
        self.assertEqual(len(self.payment_service.transactions), 0)

    @test_for("Payment fraud detection")
    @test_risk("HIGH", component="Fraud detection and payment security")
    def test_fraud_detection_workflow(self):
        """Test fraud detection prevents suspicious orders"""
        
        # Create a high-value order that should trigger fraud detection
        high_value_item = OrderItem(
            product=self.products[0], 
            quantity=20,  # High quantity to exceed fraud threshold
            unit_price=Decimal('999.99')  # High price
        )
        
        # Use different billing/shipping addresses
        different_billing = Address(
            street="456 Different St",
            city="Other City",
            state="NY",  # Different state
            zip_code="54321"
        )
        
        fraud_payment_info = PaymentInfo(
            payment_method="credit_card",
            payment_details={
                "card_number": "4111111111111111",
                "cvv": "123",
                "expiry_month": 12,
                "expiry_year": 2025
            },
            billing_address=different_billing  # Different from shipping
        )
        
        order_request = OrderRequest(
            user=self.user,
            items=[high_value_item],
            shipping_address=self.address,  # Different from billing
            payment_info=fraud_payment_info
        )
        
        # Attempt to process the order
        result = self.order_service.process_order(order_request)
        
        # Verify order failed due to fraud detection
        self.assertFalse(result.success)
        self.assertIn("FRAUD", result.error_code or "")

    @test_for("Multi-product order calculation")
    @test_invariant("Order totals are calculated correctly")
    def test_multi_product_order_calculation(self):
        """Test correct calculation of totals for multi-product orders"""
        
        # Calculate expected totals manually
        expected_subtotal = sum(item.get_total_price() for item in self.order_items)
        
        # Use order service to calculate totals
        totals = self.order_service.calculate_order_total(self.order_items, self.address)
        
        # Verify calculations
        self.assertEqual(totals["subtotal"], expected_subtotal)
        self.assertGreater(totals["tax"], Decimal('0'))
        self.assertGreater(totals["shipping"], Decimal('0'))
        self.assertEqual(
            totals["total"], 
            totals["subtotal"] + totals["tax"] + totals["shipping"]
        )

    @test_for("User order history and retrieval")
    @test_invariant("User can only access their own orders")
    @test_risk("LOW", component="Order access authorization")
    def test_user_order_history(self):
        """Test user can retrieve their order history correctly"""
        
        # Create multiple orders for the user
        order_requests = []
        for i in range(3):
            order_request = OrderRequest(
                user=self.user,
                items=[self.order_items[i % len(self.order_items)]],
                shipping_address=self.address,
                payment_info=self.payment_info
            )
            order_requests.append(order_request)
        
        # Process all orders
        order_ids = []
        for order_request in order_requests:
            result = self.order_service.process_order(order_request)
            self.assertTrue(result.success)
            order_ids.append(result.order.order_id)
        
        # Retrieve user's order history
        user_orders = self.order_service.get_user_orders(self.user.user_id)
        self.assertEqual(len(user_orders), 3)
        
        # Verify each order can be retrieved individually
        for order_id in order_ids:
            order = self.order_service.get_order(order_id, self.user.user_id)
            self.assertIsNotNone(order)
            self.assertEqual(order.user.user_id, self.user.user_id)
        
        # Verify other users cannot access these orders
        other_user_id = "other_user"
        for order_id in order_ids:
            order = self.order_service.get_order(order_id, other_user_id)
            self.assertIsNone(order)

    @test_for("Business analytics and reporting")
    def test_order_statistics_generation(self):
        """Test generation of business analytics from order data"""
        
        # Create several orders with different amounts
        test_orders = [
            (self.order_items[:1], OrderStatus.DELIVERED),
            (self.order_items[1:2], OrderStatus.SHIPPED),
            (self.order_items[2:], OrderStatus.PROCESSING)
        ]
        
        for items, final_status in test_orders:
            order_request = OrderRequest(
                user=self.user,
                items=items,
                shipping_address=self.address,
                payment_info=self.payment_info
            )
            
            result = self.order_service.process_order(order_request)
            self.assertTrue(result.success)
            
            # Update to final status if needed
            if final_status != OrderStatus.PROCESSING:
                self.order_service.update_order_status(result.order.order_id, final_status)
        
        # Get statistics
        stats = self.order_service.get_order_statistics()
        
        # Verify statistics
        self.assertEqual(stats["total_orders"], 3)
        self.assertGreater(stats["total_revenue"], Decimal('0'))
        self.assertGreater(stats["average_order_value"], Decimal('0'))
        
        # Verify status distribution
        status_dist = stats["status_distribution"]
        self.assertEqual(status_dist["delivered"], 1)
        self.assertEqual(status_dist["shipped"], 1)
        self.assertEqual(status_dist["processing"], 1)


if __name__ == '__main__':
    unittest.main()