# test_cases/dependencies/repository_pattern/base.py
class DatabaseConnection:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.is_connected = False
        self.transaction_active = False
        
    def connect(self):
        self.is_connected = True
        print(f"Connected to {self.connection_string}")
        
    def disconnect(self):
        self.is_connected = False
        print("Disconnected")
        
    def begin_transaction(self):
        self.transaction_active = True
        print("Transaction started")
        
    def commit(self):
        self.transaction_active = False
        print("Transaction committed")
        
    def rollback(self):
        self.transaction_active = False
        print("Transaction rolled back")
        
    def execute(self, query, params=None):
        print(f"Executing: {query}")
        return [{"id": 1, "name": "Product 1", "price": 99.99}]

class UnitOfWork:
    def __init__(self, connection):
        self.connection = connection
        self.products = ProductRepository(connection)
        self.orders = OrderRepository(connection)
        
    def __enter__(self):
        self.connection.connect()
        self.connection.begin_transaction()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.disconnect()
        
    def commit(self):
        self.connection.commit()
        self.connection.begin_transaction()

class ProductRepository:
    def __init__(self, connection):
        self.connection = connection
        
    def get_by_id(self, product_id):
        return self.connection.execute("SELECT * FROM products WHERE id = ?", [product_id])[0]
        
    def get_all(self):
        return self.connection.execute("SELECT * FROM products")
        
    def add(self, product):
        self.connection.execute(
            "INSERT INTO products (name, price) VALUES (?, ?)",
            [product["name"], product["price"]]
        )
        
    def update(self, product):
        self.connection.execute(
            "UPDATE products SET name = ?, price = ? WHERE id = ?",
            [product["name"], product["price"], product["id"]]
        )
        
    def delete(self, product_id):
        self.connection.execute("DELETE FROM products WHERE id = ?", [product_id])

class OrderRepository:
    def __init__(self, connection):
        self.connection = connection
        
    def get_by_id(self, order_id):
        return self.connection.execute("SELECT * FROM orders WHERE id = ?", [order_id])[0]
        
    def add(self, order):
        self.connection.execute(
            "INSERT INTO orders (customer_id, total) VALUES (?, ?)",
            [order["customer_id"], order["total"]]
        )

class OrderService:
    def __init__(self, db_connection):
        self.db_connection = db_connection
        
    def create_order(self, customer_id, products):
        with UnitOfWork(self.db_connection) as uow:
            # Calculate total
            total = sum(p["price"] for p in products)
            
            # Create order
            order = {"customer_id": customer_id, "total": total}
            uow.orders.add(order)
            
            # Update product inventory (simplified)
            for product in products:
                db_product = uow.products.get_by_id(product["id"])
                # Update product logic would go here
                uow.products.update(db_product)
                
        return order
