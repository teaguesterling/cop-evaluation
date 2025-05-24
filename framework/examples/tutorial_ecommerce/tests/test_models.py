import unittest
from decimal import Decimal
from datetime import datetime
import sys
sys.path.append('/mnt/aux-data/teague/Projects/MindMeld/cop-testing/framework')
from cop_python.testing.annotations import test_for, test_invariant, test_risk

# Import models
sys.path.append('/mnt/aux-data/teague/Projects/MindMeld/cop-testing/framework/examples/tutorial_ecommerce')
from src.models.user import User, Address
from src.models.product import Product, ProductCategory, OrderItem
from src.models.order import Order, OrderStatus, OrderRequest, PaymentInfo


class TestUserModel(unittest.TestCase):
    
    def setUp(self):
        self.address = Address(
            street="123 Main St",
            city="Anytown", 
            state="CA",
            zip_code="12345"
        )
        self.user = User(
            user_id="user123",
            email="test@example.com",
            first_name="John",
            last_name="Doe",
            credit_limit=Decimal('1000.00'),
            current_balance=Decimal('250.00'),
            addresses=[self.address],
            created_at=datetime.now()
        )

    @test_for("models.user.User.get_available_credit")
    @test_invariant("available_credit >= 0 and available_credit <= credit_limit")
    def test_available_credit_calculation(self):
        available = self.user.get_available_credit()
        self.assertEqual(available, Decimal('750.00'))
        self.assertGreaterEqual(available, Decimal('0'))
        self.assertLessEqual(available, self.user.credit_limit)

    @test_for("models.user.User.can_afford")
    @test_invariant("amount > 0")
    def test_can_afford_valid_amount(self):
        self.assertTrue(self.user.can_afford(Decimal('500.00')))
        self.assertTrue(self.user.can_afford(Decimal('750.00')))
        self.assertFalse(self.user.can_afford(Decimal('800.00')))

    @test_for("models.user.User.can_afford")
    def test_can_afford_invalid_amount(self):
        self.assertFalse(self.user.can_afford(Decimal('0')))
        self.assertFalse(self.user.can_afford(Decimal('-10')))

    @test_for("models.user.User.charge_account")
    @test_invariant("amount > 0 and self.current_balance + amount <= self.credit_limit")
    @test_risk("HIGH", component="models.user.User.charge_account")
    def test_charge_account_success(self):
        initial_balance = self.user.current_balance
        result = self.user.charge_account(Decimal('100.00'))
        self.assertTrue(result)
        self.assertEqual(self.user.current_balance, initial_balance + Decimal('100.00'))

    @test_for("models.user.User.charge_account")
    def test_charge_account_insufficient_credit(self):
        initial_balance = self.user.current_balance
        result = self.user.charge_account(Decimal('800.00'))
        self.assertFalse(result)
        self.assertEqual(self.user.current_balance, initial_balance)

    @test_for("models.user.Address.is_valid")
    @test_invariant("len(zip_code) in [5, 9] and state.isupper() and len(state) == 2")
    def test_address_validation(self):
        valid_address = Address("123 Main St", "City", "CA", "12345")
        self.assertTrue(valid_address.is_valid())
        
        invalid_zip = Address("123 Main St", "City", "CA", "123")
        self.assertFalse(invalid_zip.is_valid())
        
        invalid_state = Address("123 Main St", "City", "ca", "12345")
        self.assertFalse(invalid_state.is_valid())


class TestProductModel(unittest.TestCase):
    
    def setUp(self):
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

    @test_for("models.product.Product.get_available_inventory")
    @test_invariant("available_inventory >= 0 and available_inventory <= inventory_count")
    def test_available_inventory_calculation(self):
        available = self.product.get_available_inventory()
        self.assertEqual(available, 100)
        self.assertGreaterEqual(available, 0)
        self.assertLessEqual(available, self.product.inventory_count)

    @test_for("models.product.Product.reserve_inventory")
    @test_invariant("quantity > 0 and quantity <= available_inventory")
    @test_risk("MEDIUM", component="models.product.Product.reserve_inventory")
    def test_inventory_reservation(self):
        result = self.product.reserve_inventory(10)
        self.assertTrue(result)
        self.assertEqual(self.product.reserved_count, 10)
        self.assertEqual(self.product.get_available_inventory(), 90)

    @test_for("models.product.Product.reserve_inventory")
    def test_inventory_reservation_insufficient_stock(self):
        result = self.product.reserve_inventory(150)
        self.assertFalse(result)
        self.assertEqual(self.product.reserved_count, 0)

    @test_for("models.product.Product.has_sufficient_inventory")
    @test_invariant("quantity > 0")
    def test_sufficient_inventory_check(self):
        self.assertTrue(self.product.has_sufficient_inventory(50))
        self.assertTrue(self.product.has_sufficient_inventory(100))
        self.assertFalse(self.product.has_sufficient_inventory(150))
        self.assertFalse(self.product.has_sufficient_inventory(0))

    @test_for("models.product.OrderItem.is_valid")
    @test_invariant("quantity > 0 and unit_price > 0")
    @test_risk("LOW", component="models.product.OrderItem.is_valid")
    def test_order_item_validation(self):
        order_item = OrderItem(
            product=self.product,
            quantity=5,
            unit_price=Decimal('29.99')
        )
        self.assertTrue(order_item.is_valid())

    @test_for("models.product.OrderItem.get_total_price")
    @test_invariant("quantity > 0 and unit_price >= 0")
    def test_order_item_total_calculation(self):
        order_item = OrderItem(
            product=self.product,
            quantity=3,
            unit_price=Decimal('29.99')
        )
        total = order_item.get_total_price()
        self.assertEqual(total, Decimal('89.97'))


class TestOrderModel(unittest.TestCase):
    
    def setUp(self):
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

    @test_for("models.order.Order.calculate_total")
    @test_invariant("total_amount > 0 and total_amount == subtotal + tax_amount + shipping_cost")
    def test_order_total_calculation(self):
        order = Order(
            order_id="order123",
            user=self.user,
            items=[self.order_item],
            shipping_address=self.address,
            payment_info=self.payment_info
        )
        
        total = order.calculate_total()
        expected_subtotal = Decimal('59.98')  # 2 * 29.99
        
        self.assertEqual(order.subtotal, expected_subtotal)
        self.assertGreater(order.tax_amount, Decimal('0'))
        self.assertGreater(order.shipping_cost, Decimal('0'))
        self.assertGreater(total, expected_subtotal)
        self.assertEqual(total, order.subtotal + order.tax_amount + order.shipping_cost)

    @test_for("models.order.Order.is_valid")
    @test_invariant("len(items) > 0 and total_amount > 0")
    @test_risk("MEDIUM", component="models.order.Order.is_valid")
    def test_order_validation(self):
        order = Order(
            order_id="order123",
            user=self.user,
            items=[self.order_item],
            shipping_address=self.address,
            payment_info=self.payment_info
        )
        
        self.assertTrue(order.is_valid())

    @test_for("models.order.Order.update_status")
    @test_invariant("new_status in OrderStatus")
    @test_risk("LOW", component="models.order.Order.update_status")
    def test_order_status_transitions(self):
        order = Order(
            order_id="order123",
            user=self.user,
            items=[self.order_item],
            shipping_address=self.address,
            payment_info=self.payment_info,
            status=OrderStatus.PENDING
        )
        
        # Valid transition
        self.assertTrue(order.update_status(OrderStatus.PROCESSING))
        self.assertEqual(order.status, OrderStatus.PROCESSING)
        
        # Invalid transition
        self.assertFalse(order.update_status(OrderStatus.DELIVERED))
        self.assertEqual(order.status, OrderStatus.PROCESSING)


if __name__ == '__main__':
    unittest.main()