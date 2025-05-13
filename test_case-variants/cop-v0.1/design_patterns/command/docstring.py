from concept_python import intent, invariant, human_decision, ai_implement


class Command:
    """COP Annotations:
@intent("Define contract for executable and undoable operations")"""

    def execute(self):
        """COP Annotations:
@intent("Execute the command")"""
        pass

    def undo(self):
        """COP Annotations:
@intent("Undo the command's effects")"""
        pass


class OrderManager:
    """COP Annotations:
@intent("Manage the lifecycle of orders")"""

    def __init__(self):
        self.orders = []

    def add_order(self, order):
        """COP Annotations:
@intent("Add a new order to the system")"""
        self.orders.append(order)

    def remove_order(self, order_id):
        """COP Annotations:
@intent("Remove an order from the system")"""
        self.orders = [o for o in self.orders if o['id'] != order_id]

    def get_order(self, order_id):
        """COP Annotations:
@intent("Retrieve an order by ID")"""
        return next((o for o in self.orders if o['id'] == order_id), None)


class InventoryManager:
    """COP Annotations:
@intent("Track and manage product inventory levels")"""

    def __init__(self):
        self.inventory = {}

    def add_product(self, product_id, quantity):
        """COP Annotations:
@intent("Add quantity of a product to inventory")
@invariant("Quantity must be non-negative")"""
        if product_id in self.inventory:
            self.inventory[product_id] += quantity
        else:
            self.inventory[product_id] = quantity

    def remove_product(self, product_id, quantity):
        """COP Annotations:
@intent("Remove quantity of a product from inventory")
@invariant("Resulting quantity cannot be negative")"""
        if product_id in self.inventory:
            self.inventory[product_id] = max(0, self.inventory[product_id] -
                quantity)

    def get_quantity(self, product_id):
        """COP Annotations:
@intent("Get current quantity of a product")"""
        return self.inventory.get(product_id, 0)


class NotificationService:
    """COP Annotations:
@intent("Send notifications to users and administrators")"""

    def notify_customer(self, customer_id, message):
        """COP Annotations:
@intent("Send a notification to a customer")"""
        print(f'Notifying customer {customer_id}: {message}')

    def notify_admin(self, message):
        """COP Annotations:
@intent("Send a notification to system administrators")"""
        print(f'Notifying admin: {message}')


class CreateOrderCommand(Command):
    """COP Annotations:
@intent("Encapsulate order creation as an atomic, reversible operation")"""

    def __init__(self, order_data, order_manager, inventory_manager,
        notification_service):
        """COP Annotations:
@intent("Initialize with required data and dependencies")"""
        self.order_data = order_data
        self.order_manager = order_manager
        self.inventory_manager = inventory_manager
        self.notification_service = notification_service
        self.executed = False

    def execute(self):
        """COP Annotations:
@intent("Execute the order creation process")
@invariant("Must maintain inventory consistency")
@invariant("Must maintain order data integrity")"""
        for item in self.order_data['items']:
            product_id = item['product_id']
            quantity = item['quantity']
            if self.inventory_manager.get_quantity(product_id) < quantity:
                raise Exception(
                    f'Insufficient inventory for product {product_id}')
        for item in self.order_data['items']:
            self.inventory_manager.remove_product(item['product_id'], item[
                'quantity'])
        self.order_manager.add_order(self.order_data)
        self.notification_service.notify_customer(self.order_data[
            'customer_id'],
            f"Order {self.order_data['id']} created successfully!")
        self.executed = True

    def undo(self):
        """COP Annotations:
@intent("Reverse the order creation process")
@invariant("Must restore system to previous state")"""
        if not self.executed:
            return
        self.order_manager.remove_order(self.order_data['id'])
        for item in self.order_data['items']:
            self.inventory_manager.add_product(item['product_id'], item[
                'quantity'])
        self.notification_service.notify_customer(self.order_data[
            'customer_id'],
            f"Order {self.order_data['id']} has been cancelled.")
        self.executed = False


class CommandProcessor:
    """COP Annotations:
@intent("Process and track commands in the system")"""

    def __init__(self):
        self.command_history = []

    def execute_command(self, command):
        """COP Annotations:
@intent("Execute a command and record it if successful")
@invariant("Failed commands must not affect system state")"""
        try:
            command.execute()
            self.command_history.append(command)
            return True
        except Exception as e:
            print(f'Command execution failed: {e}')
            return False

    def undo_last_command(self):
        """COP Annotations:
@intent("Undo the most recently executed command")
@invariant("Commands must be undone in reverse order of execution")"""
        if not self.command_history:
            return False
        command = self.command_history.pop()
        command.undo()
        return True
