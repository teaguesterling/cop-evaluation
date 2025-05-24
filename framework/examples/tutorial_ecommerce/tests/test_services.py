import unittest
from decimal import Decimal
from datetime import datetime
import sys
sys.path.append('/mnt/aux-data/teague/Projects/MindMeld/cop-testing/framework')
from cop_python.testing.annotations import test_for, test_invariant, test_risk

# Import services and models
sys.path.append('/mnt/aux-data/teague/Projects/MindMeld/cop-testing/framework/examples/tutorial_ecommerce')
from src.models.user import User, Address
from src.models.product import Product, ProductCategory, OrderItem
from src.models.order import Order, OrderStatus, OrderRequest, PaymentInfo
from src.services.inventory_service import InventoryService
from src.services.payment_service import PaymentService
from src.services.notification_service import NotificationService
from src.services.order_service import OrderService


class TestInventoryService(unittest.TestCase):
    
    def setUp(self):
        self.inventory_service = InventoryService()
        self.product = Product(
            product_id="prod123",
            name="Test Product",
            description="A test product",
            price=Decimal('29.99'),
            category=ProductCategory.ELECTRONICS,
            weight_oz=8.0,
            dimensions_inches={"length": 6, "width": 4, "height": 2},
            inventory_count=100
        )
        self.inventory_service.add_product(self.product)

    @test_for("services.inventory_service.InventoryService.acquire_inventory_lock")
    @test_invariant("quantity > 0")
    @test_risk("HIGH", component="services.inventory_service.InventoryService.acquire_inventory_lock")
    def test_acquire_inventory_lock_success(self):
        lock_id = self.inventory_service.acquire_inventory_lock("prod123", 10)
        self.assertIsNotNone(lock_id)
        
        # Check lock is recorded
        self.assertIn("prod123", self.inventory_service.locks)
        self.assertEqual(len(self.inventory_service.locks["prod123"]), 1)

    @test_for("services.inventory_service.InventoryService.acquire_inventory_lock")
    def test_acquire_inventory_lock_insufficient_inventory(self):
        lock_id = self.inventory_service.acquire_inventory_lock("prod123", 150)
        self.assertIsNone(lock_id)

    @test_for("services.inventory_service.InventoryService.validate_inventory_availability")
    @test_invariant("len(items) > 0")
    @test_risk("MEDIUM", component="services.inventory_service.InventoryService.validate_inventory_availability")
    def test_validate_inventory_availability(self):
        order_item = OrderItem(
            product=self.product,
            quantity=50,
            unit_price=Decimal('29.99')
        )
        
        results = self.inventory_service.validate_inventory_availability([order_item])
        self.assertTrue(results["prod123"])

    @test_for("services.inventory_service.InventoryService.reserve_inventory_for_order")
    @test_invariant("len(items) > 0")
    @test_risk("HIGH", component="services.inventory_service.InventoryService.reserve_inventory_for_order")
    def test_reserve_inventory_for_order(self):
        order_item = OrderItem(
            product=self.product,
            quantity=10,
            unit_price=Decimal('29.99')
        )
        
        # First acquire lock
        lock_id = self.inventory_service.acquire_inventory_lock("prod123", 10)
        self.assertIsNotNone(lock_id)
        
        # Then reserve
        result = self.inventory_service.reserve_inventory_for_order([order_item], [lock_id])
        self.assertTrue(result)
        self.assertEqual(self.product.reserved_count, 10)


class TestPaymentService(unittest.TestCase):
    
    def setUp(self):
        self.payment_service = PaymentService()
        self.address = Address("123 Main St", "City", "CA", "12345")
        self.user = User(
            user_id="user123",
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            credit_limit=Decimal('1000.00'),
            current_balance=Decimal('0.00'),
            addresses=[self.address],
            created_at=datetime.now()
        )
        
        self.product = Product(
            product_id="prod123",
            name="Test Product",
            description="A test product",
            price=Decimal('29.99'),
            category=ProductCategory.ELECTRONICS,
            weight_oz=8.0,
            dimensions_inches={"length": 6, "width": 4, "height": 2},
            inventory_count=100
        )
        
        self.order_item = OrderItem(
            product=self.product,
            quantity=2,
            unit_price=Decimal('29.99')
        )
        
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
        
        self.order = Order(
            order_id="order123",
            user=self.user,
            items=[self.order_item],
            shipping_address=self.address,
            payment_info=self.payment_info
        )
        self.order.calculate_total()

    @test_for("services.payment_service.PaymentService.process_payment")
    @test_invariant("amount > 0 and amount <= order.total_amount")
    @test_risk("HIGH", component="services.payment_service.PaymentService.process_payment")
    def test_process_payment_success(self):
        result = self.payment_service.process_payment(self.order, self.payment_info)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.transaction_id)
        self.assertEqual(result.processed_amount, self.order.total_amount)

    @test_for("services.payment_service.PaymentService.process_payment")
    def test_process_payment_invalid_amount(self):
        self.order.total_amount = Decimal('0')
        result = self.payment_service.process_payment(self.order, self.payment_info)
        self.assertFalse(result.success)
        self.assertEqual(result.error_code, "INVALID_AMOUNT")

    @test_for("services.payment_service.PaymentService._perform_fraud_detection")
    @test_invariant("order.total_amount > 0")
    @test_risk("HIGH", component="services.payment_service.PaymentService._perform_fraud_detection")
    def test_fraud_detection_high_amount(self):
        self.order.total_amount = Decimal('15000')  # Over limit
        fraud_check = self.payment_service._perform_fraud_detection(self.order, self.payment_info)
        self.assertFalse(fraud_check["passed"])
        self.assertIn("limit", fraud_check["reason"].lower())

    @test_for("services.payment_service.PaymentService._validate_credit_card")
    @test_invariant("card_details contains required fields")
    @test_risk("HIGH", component="services.payment_service.PaymentService._validate_credit_card")
    def test_credit_card_validation(self):
        valid_card = {
            "card_number": "4111111111111111",
            "cvv": "123",
            "expiry_month": 12,
            "expiry_year": 2025
        }
        self.assertTrue(self.payment_service._validate_credit_card(valid_card))
        
        invalid_card = {
            "card_number": "1234",  # Too short
            "cvv": "123",
            "expiry_month": 12,
            "expiry_year": 2025
        }
        self.assertFalse(self.payment_service._validate_credit_card(invalid_card))

    @test_for("services.payment_service.PaymentService.process_refund")
    @test_invariant("amount > 0 and transaction_id exists")
    @test_risk("MEDIUM", component="services.payment_service.PaymentService.process_refund")
    def test_process_refund_success(self):
        # First process a payment
        payment_result = self.payment_service.process_payment(self.order, self.payment_info)
        self.assertTrue(payment_result.success)
        
        # Then refund it
        refund_result = self.payment_service.process_refund(
            payment_result.transaction_id,
            Decimal('10.00'),
            "Customer request"
        )
        self.assertTrue(refund_result.success)
        self.assertEqual(refund_result.refunded_amount, Decimal('10.00'))


class TestNotificationService(unittest.TestCase):
    
    def setUp(self):
        self.notification_service = NotificationService()
        self.address = Address("123 Main St", "City", "CA", "12345")
        self.user = User(
            user_id="user123",
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            credit_limit=Decimal('1000.00'),
            current_balance=Decimal('0.00'),
            addresses=[self.address],
            created_at=datetime.now()
        )
        
        self.product = Product(
            product_id="prod123",
            name="Test Product",
            description="A test product",
            price=Decimal('29.99'),
            category=ProductCategory.ELECTRONICS,
            weight_oz=8.0,
            dimensions_inches={"length": 6, "width": 4, "height": 2},
            inventory_count=100
        )
        
        self.order_item = OrderItem(
            product=self.product,
            quantity=2,
            unit_price=Decimal('29.99')
        )
        
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
        
        self.order = Order(
            order_id="order123",
            user=self.user,
            items=[self.order_item],
            shipping_address=self.address,
            payment_info=self.payment_info
        )

    @test_for("services.notification_service.NotificationService.send_order_confirmation")
    @test_invariant("order.user is not None and order.order_id is not None")
    @test_risk("LOW", component="services.notification_service.NotificationService.send_order_confirmation")
    def test_send_order_confirmation(self):
        result = self.notification_service.send_order_confirmation(self.order)
        self.assertTrue(result)
        self.assertEqual(len(self.notification_service.messages), 1)
        
        message = self.notification_service.messages[0]
        self.assertEqual(message.notification_type, "order_confirmation")
        self.assertEqual(message.recipient, self.user.email)

    @test_for("services.notification_service.NotificationService.send_low_inventory_alert")
    @test_invariant("product_id is not None and current_stock >= 0")
    @test_risk("MEDIUM", component="services.notification_service.NotificationService.send_low_inventory_alert")
    def test_send_low_inventory_alert(self):
        result = self.notification_service.send_low_inventory_alert(
            "prod123", "Test Product", 5, 10
        )
        self.assertTrue(result)
        self.assertEqual(len(self.notification_service.messages), 1)
        
        message = self.notification_service.messages[0]
        self.assertEqual(message.notification_type, "inventory_alert")


class TestOrderService(unittest.TestCase):
    
    def setUp(self):
        self.inventory_service = InventoryService()
        self.payment_service = PaymentService()
        self.notification_service = NotificationService()
        self.order_service = OrderService(
            self.inventory_service,
            self.payment_service,
            self.notification_service
        )
        
        self.address = Address("123 Main St", "City", "CA", "12345")
        self.user = User(
            user_id="user123",
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            credit_limit=Decimal('1000.00'),
            current_balance=Decimal('0.00'),
            addresses=[self.address],
            created_at=datetime.now()
        )
        
        self.product = Product(
            product_id="prod123",
            name="Test Product",
            description="A test product",
            price=Decimal('29.99'),
            category=ProductCategory.ELECTRONICS,
            weight_oz=8.0,
            dimensions_inches={"length": 6, "width": 4, "height": 2},
            inventory_count=100
        )
        self.inventory_service.add_product(self.product)
        
        self.order_item = OrderItem(
            product=self.product,
            quantity=2,
            unit_price=Decimal('29.99')
        )
        
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
        
        self.order_request = OrderRequest(
            user=self.user,
            items=[self.order_item],
            shipping_address=self.address,
            payment_info=self.payment_info
        )

    @test_for("services.order_service.OrderService.process_order")
    @test_invariant("order_request.user is not None and len(order_request.items) > 0")
    @test_risk("HIGH", component="services.order_service.OrderService.process_order")
    def test_process_order_success(self):
        result = self.order_service.process_order(self.order_request)
        self.assertTrue(result.success)
        self.assertIsNotNone(result.order)
        self.assertEqual(result.order.status, OrderStatus.PROCESSING)

    @test_for("services.order_service.OrderService.calculate_order_total")
    @test_invariant("len(items) > 0 and shipping_address is not None")
    def test_calculate_order_total(self):
        totals = self.order_service.calculate_order_total([self.order_item], self.address)
        
        self.assertIn("subtotal", totals)
        self.assertIn("tax", totals)
        self.assertIn("shipping", totals)
        self.assertIn("total", totals)
        self.assertGreater(totals["total"], totals["subtotal"])

    @test_for("services.order_service.OrderService.cancel_order")
    @test_invariant("order_id is not None")
    @test_risk("MEDIUM", component="services.order_service.OrderService.cancel_order")
    def test_cancel_order_success(self):
        # First create an order
        result = self.order_service.process_order(self.order_request)
        self.assertTrue(result.success)
        
        order_id = result.order.order_id
        user_id = self.user.user_id
        
        # Then cancel it
        cancel_result = self.order_service.cancel_order(order_id, user_id, "Customer request")
        self.assertTrue(cancel_result)
        
        # Check status was updated
        order = self.order_service.get_order(order_id, user_id)
        self.assertEqual(order.status, OrderStatus.CANCELLED)


if __name__ == '__main__':
    unittest.main()