# test_cases/debugging/buggy_cart/base.py
class Product:
    def __init__(self, product_id, name, price, category):
        self.id = product_id
        self.name = name
        self.price = price
        self.category = category
        
class ShoppingCart:
    def __init__(self):
        self.items = {}  # product_id -> quantity
        self.discounts = []
        
    def add_item(self, product, quantity=1):
        """Add a product to the cart."""
        if quantity <= 0:
            raise ValueError("Quantity must be positive")
            
        if product.id in self.items:
            # Bug 1: Overwrites quantity instead of adding to it
            self.items[product.id] = quantity
        else:
            self.items[product.id] = quantity
        
    def remove_item(self, product_id, quantity=1):
        """Remove a product from the cart."""
        if product_id not in self.items:
            return False
            
        # Bug 2: Doesn't remove item when quantity reaches 0
        self.items[product_id] -= quantity
        return True
        
    def add_discount(self, discount):
        """Add a discount to the cart."""
        self.discounts.append(discount)
        
    def calculate_subtotal(self, products):
        """Calculate cart subtotal before discounts."""
        subtotal = 0
        
        for product_id, quantity in self.items.items():
            product = self._find_product(products, product_id)
            
            if product:
                # Bug 3: Doesn't check if quantity is positive
                subtotal += product.price * quantity
                
        return subtotal
        
    def calculate_total(self, products):
        """Calculate cart total after discounts."""
        subtotal = self.calculate_subtotal(products)
        
        # Bug 4: Discount calculation error - applies discounts cumulatively
        discount_amount = 0
        for discount in self.discounts:
            # Each discount is applied to the already discounted amount
            discount_amount += discount.calculate(self, products, subtotal - discount_amount)
            
        # Bug 5: Can result in negative total
        return subtotal - discount_amount
        
    def _find_product(self, products, product_id):
        """Find a product by ID."""
        for product in products:
            if product.id == product_id:
                return product
        return None
        
class Discount:
    def calculate(self, cart, products, subtotal):
        """Calculate the discount amount."""
        pass
        
class PercentageDiscount(Discount):
    def __init__(self, percentage):
        # Bug 6: Doesn't validate percentage range
        self.percentage = percentage
        
    def calculate(self, cart, products, subtotal):
        return subtotal * (self.percentage / 100)
        
class FixedAmountDiscount(Discount):
    def __init__(self, amount):
        self.amount = amount
        
    def calculate(self, cart, products, subtotal):
        # Bug 7: Applies full discount even if it exceeds the subtotal
        return self.amount
        
class CategoryDiscount(Discount):
    def __init__(self, category, percentage):
        self.category = category
        self.percentage = percentage
        
    def calculate(self, cart, products, subtotal):
        category_total = 0
        
        for product_id, quantity in cart.items.items():
            product = cart._find_product(products, product_id)
            
            # Bug 8: Logic error in category matching (always fails)
            if product and product.category is self.category:
                category_total += product.price * quantity
                
        return category_total * (self.percentage / 100)
