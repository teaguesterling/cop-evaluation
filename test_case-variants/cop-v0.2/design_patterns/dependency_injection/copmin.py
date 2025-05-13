# test_cases/dependencies/dependency_injection/cop.py
from copmin_help import intent, invariant, human_decision, ai_implement

@intent("Manage database connections and query execution")
class Database:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        
    @intent("Execute SQL queries against the database")
    @invariant("Must sanitize inputs to prevent SQL injection")
    def execute_query(self, query):
        print(f"Executing: {query}")
        return [{"id": 1, "name": "Test"}]

@intent("Provide logging capabilities throughout the application")
class Logger:
    @intent("Record application events and messages")
    def log(self, message):
        print(f"LOG: {message}")

@intent("Access and persist user data")
class UserRepository:
    @intent("Initialize repository with required dependencies")
    @invariant("Repository must be initialized with valid database and logger")
    def __init__(self, database, logger):
        self.database = database
        self.logger = logger
    
    @intent("Retrieve user by ID")
    def get_user(self, user_id):
        self.logger.log(f"Fetching user with ID: {user_id}")
        result = self.database.execute_query(f"SELECT * FROM users WHERE id = {user_id}")
        return result[0] if result else None
        
    @intent("Persist user information to the database")
    @invariant("User must have a name property")
    def save_user(self, user):
        self.logger.log(f"Saving user: {user['name']}")
        self.database.execute_query(f"INSERT INTO users (name) VALUES ('{user['name']}')")

@intent("Provide business logic operations for user management")
class UserService:
    @intent("Initialize service with required dependencies")
    def __init__(self, user_repository):
        self.repository = user_repository
        
    @intent("Create a new user with the given name")
    @invariant("User name must not be empty")
    def create_user(self, name):
        user = {"name": name}
        self.repository.save_user(user)
        return user
        
    @intent("Retrieve detailed information about a user")
    def get_user_details(self, user_id):
        return self.repository.get_user(user_id)
