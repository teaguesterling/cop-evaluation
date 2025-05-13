from concept_python import intent, invariant, human_decision, ai_implement


class Product:
    """COP Annotations:
@intent("Store product information")"""

    def __init__(self, product_id, name, price, category):
        self.id = product_id
        self.name = name
        self.price = price
        self.category = category


class ShoppingCart:
    """COP Annotations:
@intent("Manage shopping cart contents and calculate prices")"""

    def __init__(self):
        self.items = {}
        self.discounts = []

    def add_item(self, product, quantity=1):
        """Add a product to the cart.

COP Annotations:
@intent("Add a product to the cart")
@invariant("Quantity must be positive")"""
        if quantity <= 0:
            raise ValueError('Quantity must be positive')
        if product.id in self.items:
            self.items[product.id] = quantity
        else:
            self.items[product.id] = quantity

    def remove_item(self, product_id, quantity=1):
        """Remove a product from the cart.

COP Annotations:
@intent("Remove a product from the cart")
@invariant("Item quantity cannot be negative")"""
        if product_id not in self.items:
            return False
        self.items[product_id] -= quantity
        return True

    def add_discount(self, discount):
        """Add a discount to the cart.

COP Annotations:
@intent("Add a discount to the cart")"""
        self.discounts.append(discount)

    def calculate_subtotal(self, products):
        """Calculate cart subtotal before discounts.

COP Annotations:
@intent("Calculate the cart subtotal before discounts")
@invariant("Subtotal must be non-negative")"""
        subtotal = 0
        for product_id, quantity in self.items.items():
            product = self._find_product(products, product_id)
            if product:
                subtotal += product.price * quantity
        return subtotal

    def calculate_total(self, products):
        """Calculate cart total after discounts.

COP Annotations:
@intent("Calculate the cart total after applying discounts")
@invariant("Total must be non-negative")"""
        subtotal = self.calculate_subtotal(products)
        discount_amount = 0
        for discount in self.discounts:
            discount_amount += discount.calculate(self, products, subtotal -
                discount_amount)
        return subtotal - discount_amount

    def _find_product(self, products, product_id):
        """Find a product by ID.

COP Annotations:
@intent("Find a product in the product list by ID")"""
        for product in products:
            if product.id == product_id:
                return product
        return None


class Discount:
    """COP Annotations:
@intent("Define discount calculation behavior")"""

    def calculate(self, cart, products, subtotal):
        """Calculate the discount amount.

COP Annotations:
@intent("Calculate the discount amount")"""
        pass


class PercentageDiscount(Discount):
    """COP Annotations:
@intent("Apply a percentage discount to the cart subtotal")"""

    def __init__(self, percentage):
        """COP Annotations:
@intent("Initialize with discount percentage")
@invariant("Percentage must be between 0 and 100")"""
        self.percentage = percentage

    def calculate(self, cart, products, subtotal):
        """COP Annotations:
@intent("Calculate the percentage discount")"""
        return subtotal * (self.percentage / 100)


class FixedAmountDiscount(Discount):
    """COP Annotations:
@intent("Apply a fixed amount discount to the cart")"""

    def __init__(self, amount):
        self.amount = amount

    def calculate(self, cart, products, subtotal):
        """COP Annotations:
@intent("Calculate the fixed amount discount")
@invariant("Discount cannot exceed the subtotal")"""
        return self.amount


class CategoryDiscount(Discount):
    """COP Annotations:
@intent("Apply a discount to products in a specific category")"""

    def __init__(self, category, percentage):
        self.category = category
        self.percentage = percentage

    def calculate(self, cart, products, subtotal):
        """COP Annotations:
@intent("Calculate the category-specific discount")"""
        category_total = 0
        for product_id, quantity in cart.items.items():
            product = cart._find_product(products, product_id)
            if product and product.category is self.category:
                category_total += product.price * quantity
        return category_total * (self.percentage / 100)
