from concept_python import intent, invariant, human_decision, ai_implement


class DatabaseConnection:
    """COP Annotations:
@intent("Manage database connections and transactions")"""

    def __init__(self, connection_string):
        self.connection_string = connection_string
        self.is_connected = False
        self.transaction_active = False

    def connect(self):
        """COP Annotations:
@intent("Establish connection to the database")"""
        self.is_connected = True
        print(f'Connected to {self.connection_string}')

    def disconnect(self):
        """COP Annotations:
@intent("Close the database connection")"""
        self.is_connected = False
        print('Disconnected')

    def begin_transaction(self):
        """COP Annotations:
@intent("Start a new database transaction")
@invariant("Connection must be established before beginning transaction")"""
        self.transaction_active = True
        print('Transaction started')

    def commit(self):
        """COP Annotations:
@intent("Commit the current transaction")
@invariant("Transaction must be active to commit")"""
        self.transaction_active = False
        print('Transaction committed')

    def rollback(self):
        """COP Annotations:
@intent("Roll back the current transaction")
@invariant("Transaction must be active to rollback")"""
        self.transaction_active = False
        print('Transaction rolled back')

    def execute(self, query, params=None):
        """COP Annotations:
@intent("Execute a SQL query with optional parameters")
@invariant("Connection must be established")
@ai_implement("Implement query execution with proper parameter sanitization", constraints=["Must prevent SQL injection", "Must handle connection errors gracefully", "Should use parameterized queries"])"""
        print(f'Executing: {query}')
        return [{'id': 1, 'name': 'Product 1', 'price': 99.99}]


class UnitOfWork:
    """COP Annotations:
@intent("Coordinate operations as a single transaction")"""

    def __init__(self, connection):
        """COP Annotations:
@intent("Initialize with all required repositories")"""
        self.connection = connection
        self.products = ProductRepository(connection)
        self.orders = OrderRepository(connection)

    def __enter__(self):
        """COP Annotations:
@intent("Setup the transaction context")
@invariant("Must establish connection and start transaction")"""
        self.connection.connect()
        self.connection.begin_transaction()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """COP Annotations:
@intent("Complete or rollback the transaction context")
@invariant("Must always release database resources")"""
        if exc_type is not None:
            self.connection.rollback()
        else:
            self.connection.commit()
        self.connection.disconnect()

    def commit(self):
        """COP Annotations:
@intent("Commit current changes and start a new transaction")"""
        self.connection.commit()
        self.connection.begin_transaction()


class ProductRepository:
    """COP Annotations:
@intent("Access and manipulate product data")"""

    def __init__(self, connection):
        self.connection = connection

    def get_by_id(self, product_id):
        """COP Annotations:
@intent("Retrieve a product by its ID")"""
        return self.connection.execute('SELECT * FROM products WHERE id = ?',
            [product_id])[0]

    def get_all(self):
        """COP Annotations:
@intent("Retrieve all products")"""
        return self.connection.execute('SELECT * FROM products')

    def add(self, product):
        """COP Annotations:
@intent("Add a new product to the database")
@invariant("Product must have name and price")"""
        self.connection.execute(
            'INSERT INTO products (name, price) VALUES (?, ?)', [product[
            'name'], product['price']])

    def update(self, product):
        """COP Annotations:
@intent("Update an existing product")
@invariant("Product must have id, name and price")"""
        self.connection.execute(
            'UPDATE products SET name = ?, price = ? WHERE id = ?', [
            product['name'], product['price'], product['id']])

    def delete(self, product_id):
        """COP Annotations:
@intent("Remove a product from the database")"""
        self.connection.execute('DELETE FROM products WHERE id = ?', [
            product_id])


class OrderRepository:
    """COP Annotations:
@intent("Access and manipulate order data")"""

    def __init__(self, connection):
        self.connection = connection

    def get_by_id(self, order_id):
        """COP Annotations:
@intent("Retrieve an order by its ID")"""
        return self.connection.execute('SELECT * FROM orders WHERE id = ?',
            [order_id])[0]

    def add(self, order):
        """COP Annotations:
@intent("Add a new order to the database")
@invariant("Order must have customer_id and total")"""
        self.connection.execute(
            'INSERT INTO orders (customer_id, total) VALUES (?, ?)', [order
            ['customer_id'], order['total']])


class OrderService:
    """COP Annotations:
@intent("Provide business logic for order management")"""

    def __init__(self, db_connection):
        """COP Annotations:
@intent("Initialize with required dependencies")"""
        self.db_connection = db_connection

    def create_order(self, customer_id, products):
        """COP Annotations:
@intent("Create a new order for a customer with selected products")
@invariant("Order must maintain data consistency across products and orders")
@human_decision("Define order business rules and validation logic", roles=["Business Analyst", "Sales Manager"])"""
        with UnitOfWork(self.db_connection) as uow:
            total = sum(p['price'] for p in products)
            order = {'customer_id': customer_id, 'total': total}
            uow.orders.add(order)
            for product in products:
                db_product = uow.products.get_by_id(product['id'])
                uow.products.update(db_product)
        return order
