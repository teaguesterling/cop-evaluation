# test_cases/best_practices/solid_principles/base.py
# E-commerce system with SOLID principles applied

class Product:
    def __init__(self, id, name, price):
        self.id = id
        self.name = name
        self.price = price

class Order:
    def __init__(self, id, customer_id):
        self.id = id
        self.customer_id = customer_id
        self.items = []
        self.total = 0
        
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
        
    def get_total(self):
        return self.total

class ProductRepository:
    def __init__(self, database):
        self.db = database
        
    def get_by_id(self, product_id):
        return self.db.find_product(product_id)
        
    def get_all(self):
        return self.db.get_all_products()
        
    def save(self, product):
        return self.db.save_product(product)

class OrderRepository:
    def __init__(self, database):
        self.db = database
        
    def get_by_id(self, order_id):
        return self.db.find_order(order_id)
        
    def save(self, order):
        return self.db.save_order(order)

class TaxCalculator:
    def calculate_tax(self, order, tax_rate):
        return order.get_total() * tax_rate

class ShippingCalculator:
    def calculate_shipping(self, order, shipping_rate):
        # Base shipping calculation
        return shipping_rate

class EmailService:
    def send_email(self, to, subject, body):
        # Code to send email
        print(f"Email to {to}: {subject}")

class OrderService:
    def __init__(self, order_repository, product_repository, tax_calculator, 
                 shipping_calculator, email_service):
        self.order_repository = order_repository
        self.product_repository = product_repository
        self.tax_calculator = tax_calculator
        self.shipping_calculator = shipping_calculator
        self.email_service = email_service
        
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
        
    def _generate_order_id(self):
        # Simple ID generation logic for demonstration
        import random
        return f"ORD-{random.randint(10000, 99999)}"
        
    def _send_order_confirmation(self, order, customer_id, subtotal, tax, shipping, total):
        # Sample email content
        subject = f"Order Confirmation: {order.id}"
        body = f"Thank you for your order! Total: ${total:.2f}"
        
        # Send email (in a real system, we'd get the email from customer_id)
        self.email_service.send_email(f"customer_{customer_id}@example.com", subject, body)

# Discount strategy pattern
class DiscountStrategy:
    def apply_discount(self, order):
        pass

class PercentageDiscount(DiscountStrategy):
    def __init__(self, percentage):
        self.percentage = percentage
        
    def apply_discount(self, order):
        return order.get_total() * (self.percentage / 100)

class FixedAmountDiscount(DiscountStrategy):
    def __init__(self, amount):
        self.amount = amount
        
    def apply_discount(self, order):
        return min(self.amount, order.get_total())

class OrderWithDiscountService:
    def __init__(self, order_service, discount_strategy):
        self.order_service = order_service
        self.discount_strategy = discount_strategy
        
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
