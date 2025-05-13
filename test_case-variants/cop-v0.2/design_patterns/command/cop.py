# test_cases/dependencies/command_pattern/cop.py
from cop_python import intent, invariant, human_decision, ai_implement

@intent("Define contract for executable and undoable operations")
class Command:
    @intent("Execute the command")
    def execute(self):
        pass
        
    @intent("Undo the command's effects")
    def undo(self):
        pass

@intent("Manage the lifecycle of orders")
class OrderManager:
    def __init__(self):
        self.orders = []
        
    @intent("Add a new order to the system")
    def add_order(self, order):
        self.orders.append(order)
        
    @intent("Remove an order from the system")
    def remove_order(self, order_id):
        self.orders = [o for o in self.orders if o["id"] != order_id]
        
    @intent("Retrieve an order by ID")
    def get_order(self, order_id):
        return next((o for o in self.orders if o["id"] == order_id), None)

@intent("Track and manage product inventory levels")
class InventoryManager:
    def __init__(self):
        self.inventory = {}
        
    @intent("Add quantity of a product to inventory")
    @invariant("Quantity must be non-negative")
    def add_product(self, product_id, quantity):
        if product_id in self.inventory:
            self.inventory[product_id] += quantity
        else:
            self.inventory[product_id] = quantity
            
    @intent("Remove quantity of a product from inventory")
    @invariant("Resulting quantity cannot be negative")
    def remove_product(self, product_id, quantity):
        if product_id in self.inventory:
            self.inventory[product_id] = max(0, self.inventory[product_id] - quantity)
            
    @intent("Get current quantity of a product")
    def get_quantity(self, product_id):
        return self.inventory.get(product_id, 0)

@intent("Send notifications to users and administrators")
class NotificationService:
    @intent("Send a notification to a customer")
    def notify_customer(self, customer_id, message):
        print(f"Notifying customer {customer_id}: {message}")
        
    @intent("Send a notification to system administrators")
    def notify_admin(self, message):
        print(f"Notifying admin: {message}")

@intent("Encapsulate order creation as an atomic, reversible operation")
class CreateOrderCommand(Command):
    @intent("Initialize with required data and dependencies")
    def __init__(self, order_data, order_manager, inventory_manager, notification_service):
        self.order_data = order_data
        self.order_manager = order_manager
        self.inventory_manager = inventory_manager
        self.notification_service = notification_service
        self.executed = False
        
    @intent("Execute the order creation process")
    @invariant("Must maintain inventory consistency")
    @invariant("Must maintain order data integrity")
    def execute(self):
        # Check inventory
        for item in self.order_data["items"]:
            product_id = item["product_id"]
            quantity = item["quantity"]
            
            if self.inventory_manager.get_quantity(product_id) < quantity:
                raise Exception(f"Insufficient inventory for product {product_id}")
                
        # Update inventory
        for item in self.order_data["items"]:
            self.inventory_manager.remove_product(item["product_id"], item["quantity"])
            
        # Add order
        self.order_manager.add_order(self.order_data)
        
        # Notify
        self.notification_service.notify_customer(
            self.order_data["customer_id"],
            f"Order {self.order_data['id']} created successfully!"
        )
        
        self.executed = True
        
    @intent("Reverse the order creation process")
    @invariant("Must restore system to previous state")
    def undo(self):
        if not self.executed:
            return
            
        # Remove order
        self.order_manager.remove_order(self.order_data["id"])
        
        # Restore inventory
        for item in self.order_data["items"]:
            self.inventory_manager.add_product(item["product_id"], item["quantity"])
            
        # Notify
        self.notification_service.notify_customer(
            self.order_data["customer_id"],
            f"Order {self.order_data['id']} has been cancelled."
        )
        
        self.executed = False

@intent("Process and track commands in the system")
class CommandProcessor:
    def __init__(self):
        self.command_history = []
        
    @intent("Execute a command and record it if successful")
    @invariant("Failed commands must not affect system state")
    def execute_command(self, command):
        try:
            command.execute()
            self.command_history.append(command)
            return True
        except Exception as e:
            print(f"Command execution failed: {e}")
            return False
            
    @intent("Undo the most recently executed command")
    @invariant("Commands must be undone in reverse order of execution")
    def undo_last_command(self):
        if not self.command_history:
            return False
            
        command = self.command_history.pop()
        command.undo()
        return True
