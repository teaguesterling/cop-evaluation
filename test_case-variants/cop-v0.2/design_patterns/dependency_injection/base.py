# test_cases/dependencies/dependency_injection/base.py
class Database:
    def __init__(self, connection_string):
        self.connection_string = connection_string
        
    def execute_query(self, query):
        print(f"Executing: {query}")
        return [{"id": 1, "name": "Test"}]

class Logger:
    def log(self, message):
        print(f"LOG: {message}")

class UserRepository:
    def __init__(self, database, logger):
        self.database = database
        self.logger = logger
    
    def get_user(self, user_id):
        self.logger.log(f"Fetching user with ID: {user_id}")
        result = self.database.execute_query(f"SELECT * FROM users WHERE id = {user_id}")
        return result[0] if result else None
        
    def save_user(self, user):
        self.logger.log(f"Saving user: {user['name']}")
        self.database.execute_query(f"INSERT INTO users (name) VALUES ('{user['name']}')")

class UserService:
    def __init__(self, user_repository):
        self.repository = user_repository
        
    def create_user(self, name):
        user = {"name": name}
        self.repository.save_user(user)
        return user
        
    def get_user_details(self, user_id):
        return self.repository.get_user(user_id)
