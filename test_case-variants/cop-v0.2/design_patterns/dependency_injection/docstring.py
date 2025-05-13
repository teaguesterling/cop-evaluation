from concept_python import intent, invariant, human_decision, ai_implement


class Database:
    """COP Annotations:
@intent("Manage database connections and query execution")"""

    def __init__(self, connection_string):
        self.connection_string = connection_string

    def execute_query(self, query):
        """COP Annotations:
@intent("Execute SQL queries against the database")
@invariant("Must sanitize inputs to prevent SQL injection")"""
        print(f'Executing: {query}')
        return [{'id': 1, 'name': 'Test'}]


class Logger:
    """COP Annotations:
@intent("Provide logging capabilities throughout the application")"""

    def log(self, message):
        """COP Annotations:
@intent("Record application events and messages")"""
        print(f'LOG: {message}')


class UserRepository:
    """COP Annotations:
@intent("Access and persist user data")"""

    def __init__(self, database, logger):
        """COP Annotations:
@intent("Initialize repository with required dependencies")
@invariant("Repository must be initialized with valid database and logger")"""
        self.database = database
        self.logger = logger

    def get_user(self, user_id):
        """COP Annotations:
@intent("Retrieve user by ID")"""
        self.logger.log(f'Fetching user with ID: {user_id}')
        result = self.database.execute_query(
            f'SELECT * FROM users WHERE id = {user_id}')
        return result[0] if result else None

    def save_user(self, user):
        """COP Annotations:
@intent("Persist user information to the database")
@invariant("User must have a name property")"""
        self.logger.log(f"Saving user: {user['name']}")
        self.database.execute_query(
            f"INSERT INTO users (name) VALUES ('{user['name']}')")


class UserService:
    """COP Annotations:
@intent("Provide business logic operations for user management")"""

    def __init__(self, user_repository):
        """COP Annotations:
@intent("Initialize service with required dependencies")"""
        self.repository = user_repository

    def create_user(self, name):
        """COP Annotations:
@intent("Create a new user with the given name")
@invariant("User name must not be empty")"""
        user = {'name': name}
        self.repository.save_user(user)
        return user

    def get_user_details(self, user_id):
        """COP Annotations:
@intent("Retrieve detailed information about a user")"""
        return self.repository.get_user(user_id)
