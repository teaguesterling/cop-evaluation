from concept_python import intent, invariant, human_decision, ai_implement


class Product:
    """COP Annotations:
@intent("Store product information and pricing")"""

    def __init__(self, id, name, price):
        self.id = id
        self.name = name
        self.price = price


class Order:
    """COP Annotations:
@intent("Represent a customer's order with products and quantities")"""

    def __init__(self, id, customer_id):
        """COP Annotations:
@intent("Initialize a new order")"""
        self.id = id
        self.customer_id = customer_id
        self.items = []
        self.total = 0

    def add_item(self, product, quantity):
        """COP Annotations:
@intent("Add a product to this order with specified quantity")
@invariant("Product must have valid price")
@invariant("Quantity must be positive")"""
        item = {'product_id': product.id, 'name': product.name, 'price':
            product.price, 'quantity': quantity, 'subtotal': product.price *
            quantity}
        self.items.append(item)
        self.total += item['subtotal']

    def get_total(self):
        """COP Annotations:
@intent("Calculate the total value of all items in the order")"""
        return self.total


class ProductRepository:
    """COP Annotations:
@intent("Provide data access for products")"""

    def __init__(self, database):
        self.db = database

    def get_by_id(self, product_id):
        """COP Annotations:
@intent("Retrieve a product by its ID")"""
        return self.db.find_product(product_id)

    def get_all(self):
        """COP Annotations:
@intent("Retrieve all available products")"""
        return self.db.get_all_products()

    def save(self, product):
        """COP Annotations:
@intent("Save or update a product")"""
        return self.db.save_product(product)


class OrderRepository:
    """COP Annotations:
@intent("Provide data access for orders")"""

    def __init__(self, database):
        self.db = database

    def get_by_id(self, order_id):
        """COP Annotations:
@intent("Retrieve an order by its ID")"""
        return self.db.find_order(order_id)

    def save(self, order):
        """COP Annotations:
@intent("Save or update an order")"""
        return self.db.save_order(order)


class TaxCalculator:
    """COP Annotations:
@intent("Calculate tax amount for an order")"""

    def calculate_tax(self, order, tax_rate):
        """COP Annotations:
@intent("Apply tax rate to order total")
@invariant("Tax calculation must be accurate to two decimal places")"""
        return order.get_total() * tax_rate


class ShippingCalculator:
    """COP Annotations:
@intent("Calculate shipping costs for an order")"""

    def calculate_shipping(self, order, shipping_rate):
        """COP Annotations:
@intent("Calculate shipping based on order and rate")
@invariant("Shipping costs must never be negative")"""
        return shipping_rate


class EmailService:
    """COP Annotations:
@intent("Send email notifications")"""

    def send_email(self, to, subject, body):
        """COP Annotations:
@intent("Send an email message")
@ai_implement("Implement email sending functionality", constraints=["Must validate email address format", "Must handle sending failures gracefully", "Must support text and HTML content"])"""
        print(f'Email to {to}: {subject}')


class OrderService:
    """COP Annotations:
@intent("Coordinate order creation and processing")"""

    def __init__(self, order_repository, product_repository, tax_calculator,
        shipping_calculator, email_service):
        """COP Annotations:
@intent("Initialize with required dependencies")"""
        self.order_repository = order_repository
        self.product_repository = product_repository
        self.tax_calculator = tax_calculator
        self.shipping_calculator = shipping_calculator
        self.email_service = email_service

    def create_order(self, customer_id, product_ids, tax_rate, shipping_rate):
        """COP Annotations:
@intent("Create and process a new customer order")
@invariant("Order must contain valid products")
@invariant("Customer must exist")"""
        order_id = self._generate_order_id()
        order = Order(order_id, customer_id)
        for product_id in product_ids:
            product = self.product_repository.get_by_id(product_id)
            if product:
                order.add_item(product, 1)
        self.order_repository.save(order)
        subtotal = order.get_total()
        tax = self.tax_calculator.calculate_tax(order, tax_rate)
        shipping = self.shipping_calculator.calculate_shipping(order,
            shipping_rate)
        total = subtotal + tax + shipping
        self._send_order_confirmation(order, customer_id, subtotal, tax,
            shipping, total)
        return {'order_id': order_id, 'subtotal': subtotal, 'tax': tax,
            'shipping': shipping, 'total': total}

    def _generate_order_id(self):
        """COP Annotations:
@intent("Generate a unique order identifier")"""
        import random
        return f'ORD-{random.randint(10000, 99999)}'

    def _send_order_confirmation(self, order, customer_id, subtotal, tax,
        shipping, total):
        """COP Annotations:
@intent("Send order confirmation to customer")"""
        subject = f'Order Confirmation: {order.id}'
        body = f'Thank you for your order! Total: ${total:.2f}'
        self.email_service.send_email(f'customer_{customer_id}@example.com',
            subject, body)


class DiscountStrategy:
    """COP Annotations:
@intent("Define discount calculation behavior")"""

    def apply_discount(self, order):
        """COP Annotations:
@intent("Apply discount to an order")"""
        pass


class PercentageDiscount(DiscountStrategy):
    """COP Annotations:
@intent("Apply percentage-based discount")"""

    def __init__(self, percentage):
        """COP Annotations:
@intent("Initialize with discount percentage")"""
        self.percentage = percentage

    def apply_discount(self, order):
        """COP Annotations:
@intent("Apply percentage discount to order total")
@invariant("Percentage must be between 0 and 100")"""
        return order.get_total() * (self.percentage / 100)


class FixedAmountDiscount(DiscountStrategy):
    """COP Annotations:
@intent("Apply fixed amount discount")"""

    def __init__(self, amount):
        """COP Annotations:
@intent("Initialize with fixed discount amount")"""
        self.amount = amount

    def apply_discount(self, order):
        """COP Annotations:
@intent("Apply fixed amount discount to order total")
@invariant("Discount cannot exceed order total")"""
        return min(self.amount, order.get_total())


class OrderWithDiscountService:
    """COP Annotations:
@intent("Process orders with discount application")"""

    def __init__(self, order_service, discount_strategy):
        """COP Annotations:
@intent("Initialize with required services")"""
        self.order_service = order_service
        self.discount_strategy = discount_strategy

    def create_order_with_discount(self, customer_id, product_ids, tax_rate,
        shipping_rate):
        """COP Annotations:
@intent("Create an order with discount applied")
@human_decision("Define discount strategy and parameters", roles=["Marketing Manager", "Sales Director"])"""
        order_data = self.order_service.create_order(customer_id,
            product_ids, tax_rate, shipping_rate)
        order = Order(order_data['order_id'], customer_id)
        discount_amount = self.discount_strategy.apply_discount(order)
        new_total = order_data['total'] - discount_amount
        return {**order_data, 'discount': discount_amount, 'final_total':
            new_total}
