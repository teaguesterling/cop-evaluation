# test_cases/best_practices/solid_principles/cop.py
from cop_python import intent, invariant, human_decision, ai_implement

# E-commerce system with SOLID principles applied and COP annotations

@intent("Store product information and pricing")
class Product:
    def __init__(self, id, name, price):
        self.id = id
        self.name = name
        self.price = price

@intent("Represent a customer's order with products and quantities")
class Order:
    @intent("Initialize a new order")
    def __init__(self, id, customer_id):
        self.id = id
        self.customer_id = customer_id
        self.items = []
        self.total = 0
        
    @intent("Add a product to this order with specified quantity")
    @invariant("Product must have valid price")
    @invariant("Quantity must be positive")
    def add_item(self, product, quantity):
        item = {
            'product_id': product.id,
            'name': product.name,
            'price': product.price,
            'quantity': quantity,
            'subtotal': product.price * quantity
        }
        self.items.append(item)
        self.total += item['subtotal']
        
    @intent("Calculate the total value of all items in the order")
    def get_total(self):
        return self.total

@intent("Provide data access for products")
class ProductRepository:
    def __init__(self, database):
        self.db = database
        
    @intent("Retrieve a product by its ID")
    def get_by_id(self, product_id):
        return self.db.find_product(product_id)
        
    @intent("Retrieve all available products")
    def get_all(self):
        return self.db.get_all_products()
        
    @intent("Save or update a product")
    def save(self, product):
        return self.db.save_product(product)

@intent("Provide data access for orders")
class OrderRepository:
    def __init__(self, database):
        self.db = database
        
    @intent("Retrieve an order by its ID")
    def get_by_id(self, order_id):
        return self.db.find_order(order_id)
        
    @intent("Save or update an order")
    def save(self, order):
        return self.db.save_order(order)

@intent("Calculate tax amount for an order")
class TaxCalculator:
    @intent("Apply tax rate to order total")
    @invariant("Tax calculation must be accurate to two decimal places")
    def calculate_tax(self, order, tax_rate):
        return order.get_total() * tax_rate

@intent("Calculate shipping costs for an order")
class ShippingCalculator:
    @intent("Calculate shipping based on order and rate")
    @invariant("Shipping costs must never be negative")
    def calculate_shipping(self, order, shipping_rate):
        # Base shipping calculation
        return shipping_rate

@intent("Send email notifications")
class EmailService:
    @intent("Send an email message")
    @ai_implement("Implement email sending functionality",
                 constraints=["Must validate email address format",
                              "Must handle sending failures gracefully",
                              "Must support text and HTML content"])
    def send_email(self, to, subject, body):
        # Code to send email
        print(f"Email to {to}: {subject}")

@intent("Coordinate order creation and processing")
class OrderService:
    @intent("Initialize with required dependencies")
    def __init__(self, order_repository, product_repository, tax_calculator, 
                 shipping_calculator, email_service):
        self.order_repository = order_repository
        self.product_repository = product_repository
        self.tax_calculator = tax_calculator
        self.shipping_calculator = shipping_calculator
        self.email_service = email_service
        
    @intent("Create and process a new customer order")
    @invariant("Order must contain valid products")
    @invariant("Customer must exist")
    def create_order(self, customer_id, product_ids, tax_rate, shipping_rate):
        # Create new order
        order_id = self._generate_order_id()
        order = Order(order_id, customer_id)
        
        # Add items
        for product_id in product_ids:
            product = self.product_repository.get_by_id(product_id)
            if product:
                order.add_item(product, 1)  # Assuming quantity 1 for simplicity
        
        # Save order
        self.order_repository.save(order)
        
        # Calculate final costs
        subtotal = order.get_total()
        tax = self.tax_calculator.calculate_tax(order, tax_rate)
        shipping = self.shipping_calculator.calculate_shipping(order, shipping_rate)
        total = subtotal + tax + shipping
        
        # Notify customer
        self._send_order_confirmation(order, customer_id, subtotal, tax, shipping, total)
        
        return {
            'order_id': order_id,
            'subtotal': subtotal,
            'tax': tax,
            'shipping': shipping,
            'total': total
        }
        
    @intent("Generate a unique order identifier")
    def _generate_order_id(self):
        # Simple ID generation logic for demonstration
        import random
        return f"ORD-{random.randint(10000, 99999)}"
        
    @intent("Send order confirmation to customer")
    def _send_order_confirmation(self, order, customer_id, subtotal, tax, shipping, total):
        # Sample email content
        subject = f"Order Confirmation: {order.id}"
        body = f"Thank you for your order! Total: ${total:.2f}"
        
        # Send email (in a real system, we'd get the email from customer_id)
        self.email_service.send_email(f"customer_{customer_id}@example.com", subject, body)

# Discount strategy pattern
@intent("Define discount calculation behavior")
class DiscountStrategy:
    @intent("Apply discount to an order")
    def apply_discount(self, order):
        pass

@intent("Apply percentage-based discount")
class PercentageDiscount(DiscountStrategy):
    @intent("Initialize with discount percentage")
    def __init__(self, percentage):
        self.percentage = percentage
        
    @intent("Apply percentage discount to order total")
    @invariant("Percentage must be between 0 and 100")
    def apply_discount(self, order):
        return order.get_total() * (self.percentage / 100)

@intent("Apply fixed amount discount")
class FixedAmountDiscount(DiscountStrategy):
    @intent("Initialize with fixed discount amount")
    def __init__(self, amount):
        self.amount = amount
        
    @intent("Apply fixed amount discount to order total")
    @invariant("Discount cannot exceed order total")
    def apply_discount(self, order):
        return min(self.amount, order.get_total())

@intent("Process orders with discount application")
class OrderWithDiscountService:
    @intent("Initialize with required services")
    def __init__(self, order_service, discount_strategy):
        self.order_service = order_service
        self.discount_strategy = discount_strategy
        
    @intent("Create an order with discount applied")
    @human_decision("Define discount strategy and parameters",
                   roles=["Marketing Manager", "Sales Director"])
    def create_order_with_discount(self, customer_id, product_ids, tax_rate, shipping_rate):
        # Create regular order first
        order_data = self.order_service.create_order(customer_id, product_ids, tax_rate, shipping_rate)
        
        # Get the order from repository
        order = Order(order_data['order_id'], customer_id)
        
        # Apply discount
        discount_amount = self.discount_strategy.apply_discount(order)
        
        # Update totals
        new_total = order_data['total'] - discount_amount
        
        # In a real system, we'd update the order in the repository
        
        return {
            **order_data,
            'discount': discount_amount,
            'final_total': new_total
        }
