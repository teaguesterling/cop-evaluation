from concept_python import intent, invariant, human_decision, ai_implement


class SuperController:
    """COP Annotations:
@intent("Manage all e-commerce operations including users, products, orders, and payments")"""

    def __init__(self):
        self.users = []
        self.products = []
        self.orders = []
        self.payments = []
        self.settings = {'tax_rate': 0.07, 'shipping_cost': 5.99,
            'discount_threshold': 100, 'bulk_discount': 0.1}

    def add_user(self, name, email, address):
        """COP Annotations:
@intent("Add a new user to the system")
@invariant("Email must be unique")"""
        user_id = len(self.users) + 1
        user = {'id': user_id, 'name': name, 'email': email, 'address':
            address, 'orders': []}
        self.users.append(user)
        return user_id

    def update_user(self, user_id, name=None, email=None, address=None):
        """COP Annotations:
@intent("Update an existing user's information")"""
        for user in self.users:
            if user['id'] == user_id:
                if name:
                    user['name'] = name
                if email:
                    user['email'] = email
                if address:
                    user['address'] = address
                return True
        return False

    def get_user(self, user_id):
        """COP Annotations:
@intent("Retrieve a user by ID")"""
        for user in self.users:
            if user['id'] == user_id:
                return user
        return None

    def add_product(self, name, price, inventory):
        """COP Annotations:
@intent("Add a new product to the catalog")
@invariant("Product price must be positive")
@invariant("Product inventory must be non-negative")"""
        product_id = len(self.products) + 1
        product = {'id': product_id, 'name': name, 'price': price,
            'inventory': inventory}
        self.products.append(product)
        return product_id

    def update_product(self, product_id, name=None, price=None, inventory=None
        ):
        """COP Annotations:
@intent("Update an existing product's information")"""
        for product in self.products:
            if product['id'] == product_id:
                if name:
                    product['name'] = name
                if price is not None:
                    product['price'] = price
                if inventory is not None:
                    product['inventory'] = inventory
                return True
        return False

    def get_product(self, product_id):
        """COP Annotations:
@intent("Retrieve a product by ID")"""
        for product in self.products:
            if product['id'] == product_id:
                return product
        return None

    def create_order(self, user_id, product_ids):
        """COP Annotations:
@intent("Create a new order for a user")
@invariant("Order must have at least one product")
@invariant("Products must be in stock")
@invariant("User must exist")
@human_decision("Define discount and pricing rules", roles=["Sales Manager", "Marketing Director"])"""
        user = self.get_user(user_id)
        if not user:
            return {'error': 'User not found'}
        order_items = []
        total = 0
        for product_id in product_ids:
            product = self.get_product(product_id)
            if not product:
                return {'error': f'Product {product_id} not found'}
            if product['inventory'] <= 0:
                return {'error': f'Product {product_id} out of stock'}
            order_items.append({'product_id': product_id, 'name': product[
                'name'], 'price': product['price']})
            total += product['price']
            product['inventory'] -= 1
        if total > self.settings['discount_threshold']:
            total = total * (1 - self.settings['bulk_discount'])
        tax = total * self.settings['tax_rate']
        total_with_tax = total + tax
        final_total = total_with_tax + self.settings['shipping_cost']
        order_id = len(self.orders) + 1
        order = {'id': order_id, 'user_id': user_id, 'items': order_items,
            'subtotal': total, 'tax': tax, 'shipping': self.settings[
            'shipping_cost'], 'total': final_total, 'status': 'pending'}
        self.orders.append(order)
        user['orders'].append(order_id)
        return {'order_id': order_id, 'total': final_total}

    def process_payment(self, order_id, payment_method, payment_details):
        """COP Annotations:
@intent("Process payment for an existing order")
@invariant("Order must exist and be in pending status")
@ai_implement("Implement payment processing logic", constraints=["Must validate payment details", "Must update order status atomically", "Must handle payment failures gracefully"])"""
        order = None
        for o in self.orders:
            if o['id'] == order_id:
                order = o
                break
        if not order:
            return {'error': 'Order not found'}
        if order['status'] != 'pending':
            return {'error': 'Order already processed'}
        payment_id = len(self.payments) + 1
        payment = {'id': payment_id, 'order_id': order_id, 'amount': order[
            'total'], 'method': payment_method, 'details': payment_details,
            'status': 'completed'}
        self.payments.append(payment)
        order['status'] = 'paid'
        order['payment_id'] = payment_id
        user = self.get_user(order['user_id'])
        self.send_email(user['email'], 'Order Confirmation',
            f"Your order #{order_id} has been processed. Total: ${order['total']:.2f}"
            )
        return {'payment_id': payment_id, 'status': 'completed'}

    def send_email(self, to, subject, body):
        """COP Annotations:
@intent("Send an email notification")"""
        print(f'Email to {to}: {subject} - {body}')

    def generate_invoice(self, order_id):
        """COP Annotations:
@intent("Generate an invoice for an order")"""
        order = None
        for o in self.orders:
            if o['id'] == order_id:
                order = o
                break
        if not order:
            return {'error': 'Order not found'}
        user = self.get_user(order['user_id'])
        invoice = (
            f"INVOICE\n\nOrder: #{order_id}\nCustomer: {user['name']}\n\n")
        invoice += 'Items:\n'
        for item in order['items']:
            invoice += f"- {item['name']}: ${item['price']:.2f}\n"
        invoice += f"\nSubtotal: ${order['subtotal']:.2f}"
        invoice += f"\nTax: ${order['tax']:.2f}"
        invoice += f"\nShipping: ${order['shipping']:.2f}"
        invoice += f"\nTotal: ${order['total']:.2f}"
        return invoice

    def update_settings(self, settings):
        """COP Annotations:
@intent("Update system configuration settings")
@human_decision("Define system-wide business rules", roles=["Business Administrator", "Financial Officer"])"""
        for key, value in settings.items():
            if key in self.settings:
                self.settings[key] = value
