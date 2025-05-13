# test_cases/dependencies/repository_pattern/cop.py
from cop_python import intent, invariant, human_decision, ai_implement

@intent("Manage database connections and transactions")
class DatabaseConnection:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.is_connected = False
        self.transaction_active = False
        
    @intent("Establish connection to the database")
    def connect(self):
        self.is_connected = True
        print(f"Connected to {self.connection_string}")
        
    @intent("Close the database connection")
    def disconnect(self):
        self.is_connected = False
        print("Disconnected")
        
    @intent("Start a new database transaction")
    @invariant("Connection must be established before beginning transaction")
    def begin_transaction(self):
        self.transaction_active = True
        print("Transaction started")
        
    @intent("Commit the current transaction")
    @invariant("Transaction must be active to commit")
    def commit(self):
        self.transaction_active = False
        print("Transaction committed")
        
    @intent("Roll back the current transaction")
    @invariant("Transaction must be active to rollback")
    def rollback(self):
        self.transaction_active = False
        print("Transaction rolled back")
        
    @intent("Execute a SQL query with optional parameters")
    @invariant("Connection must be established")
    @ai_implement("Implement query execution with proper parameter sanitization",
                constraints=["Must prevent SQL injection",
                            "Must handle connection errors gracefully",
                            "Should use parameterized queries"])
    def execute(self, query, params=None):
        print(f"Executing: {query}")
        return [{"id": 1, "name": "Product 1", "price": 99.99}]

@intent("Coordinate operations as a single transaction")
class UnitOfWork:
    @intent("Initialize with all required repositories")
    def __init__(self, connection):
        self.connection = connection
        self.products = ProductRepository(connection)
        self.orders = OrderRepository(connection)
        
    @intent("Setup the transaction context")
    @invariant("Must establish connection and start transaction")
    def __enter__(self):
        self.connection.connect()
        self.connection.begin_transaction()
        return self
        
    @intent("Complete or rollback the transaction context")
    @invariant("Must always release database resources")
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.disconnect()
        
    @intent("Commit current changes and start a new transaction")
    def commit(self):
        self.connection.commit()
        self.connection.begin_transaction()

@intent("Access and manipulate product data")
class ProductRepository:
    def __init__(self, connection):
        self.connection = connection
        
    @intent("Retrieve a product by its ID")
    def get_by_id(self, product_id):
        return self.connection.execute("SELECT * FROM products WHERE id = ?", [product_id])[0]
        
    @intent("Retrieve all products")
    def get_all(self):
        return self.connection.execute("SELECT * FROM products")
        
    @intent("Add a new product to the database")
    @invariant("Product must have name and price")
    def add(self, product):
        self.connection.execute(
            "INSERT INTO products (name, price) VALUES (?, ?)",
            [product["name"], product["price"]]
        )
        
    @intent("Update an existing product")
    @invariant("Product must have id, name and price")
    def update(self, product):
        self.connection.execute(
            "UPDATE products SET name = ?, price = ? WHERE id = ?",
            [product["name"], product["price"], product["id"]]
        )
        
    @intent("Remove a product from the database")
    def delete(self, product_id):
        self.connection.execute("DELETE FROM products WHERE id = ?", [product_id])

@intent("Access and manipulate order data")
class OrderRepository:
    def __init__(self, connection):
        self.connection = connection
        
    @intent("Retrieve an order by its ID")
    def get_by_id(self, order_id):
        return self.connection.execute("SELECT * FROM orders WHERE id = ?", [order_id])[0]
        
    @intent("Add a new order to the database")
    @invariant("Order must have customer_id and total")
    def add(self, order):
        self.connection.execute(
            "INSERT INTO orders (customer_id, total) VALUES (?, ?)",
            [order["customer_id"], order["total"]]
        )

@intent("Provide business logic for order management")
class OrderService:
    @intent("Initialize with required dependencies")
    def __init__(self, db_connection):
        self.db_connection = db_connection
        
    @intent("Create a new order for a customer with selected products")
    @invariant("Order must maintain data consistency across products and orders")
    @human_decision("Define order business rules and validation logic",
                   roles=["Business Analyst", "Sales Manager"])
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
