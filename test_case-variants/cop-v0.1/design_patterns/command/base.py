# test_cases/dependencies/command_pattern/base.py
class Command:
    def execute(self):
        pass
        
    def undo(self):
        pass

class OrderManager:
    def __init__(self):
        self.orders = []
        
    def add_order(self, order):
        self.orders.append(order)
        
    def remove_order(self, order_id):
        self.orders = [o for o in self.orders if o["id"] != order_id]
        
    def get_order(self, order_id):
        return next((o for o in self.orders if o["id"] == order_id), None)

class InventoryManager:
    def __init__(self):
        self.inventory = {}
        
    def add_product(self, product_id, quantity):
        if product_id in self.inventory:
            self.inventory[product_id] += quantity
        else:
            self.inventory[product_id] = quantity
            
    def remove_product(self, product_id, quantity):
        if product_id in self.inventory:
            self.inventory[product_id] = max(0, self.inventory[product_id] - quantity)
            
    def get_quantity(self, product_id):
        return self.inventory.get(product_id, 0)

class NotificationService:
    def notify_customer(self, customer_id, message):
        print(f"Notifying customer {customer_id}: {message}")
        
    def notify_admin(self, message):
        print(f"Notifying admin: {message}")

class CreateOrderCommand(Command):
    def __init__(self, order_data, order_manager, inventory_manager, notification_service):
        self.order_data = order_data
        self.order_manager = order_manager
        self.inventory_manager = inventory_manager
        self.notification_service = notification_service
        self.executed = False
        
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

class CommandProcessor:
    def __init__(self):
        self.command_history = []
        
    def execute_command(self, command):
        try:
            command.execute()
            self.command_history.append(command)
            return True
        except Exception as e:
            print(f"Command execution failed: {e}")
            return False
            
    def undo_last_command(self):
        if not self.command_history:
            return False
            
        command = self.command_history.pop()
        command.undo()
        return True
