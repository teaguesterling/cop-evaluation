# test_cases/debugging/buggy_auth/cop.py
import hashlib
import random
import time

# @intent("Store user account information")
class User:
    def __init__(self, username, password_hash, email, role="user"):
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.role = role
        self.login_attempts = 0
        self.locked = False
        self.reset_token = None
        self.reset_expiry = None
        
# @intent("Store and retrieve user data")
class UserDatabase:
    def __init__(self):
        self.users = {}
#     @intent("Add a new user to the database")
#     @invariant("Username must be unique")
#     @invariant("Username must be unique")
    def add_user(self, user):
        # Bug 1: Doesn't check if username already exists
        self.users[user.username] = user
        
#     @intent("Retrieve a user by username")
    def get_user(self, username):
        return self.users.get(username)
        
#     @intent("Update an existing user's information")
    def update_user(self, user):
        if user.username in self.users:
            self.users[user.username] = user
            
# @intent("Provide user authentication and session management")
class AuthenticationService:
    def __init__(self, user_db):
        self.user_db = user_db
        self.max_login_attempts = 5
#     @intent("Register a new user account")
#     @invariant("Username must be unique")
#     @invariant("Password must meet security requirements")
#     @invariant("Username must be unique")
#     @invariant("Password must meet security requirements")
    def register(self, username, password, email):
        """Register a new user."""
        # Bug 2: Password not validated for strength
        
        # Bug 3: Weak hash function (MD5)
        password_hash = hashlib.md5(password.encode()).hexdigest()
        
        new_user = User(username, password_hash, email)
        self.user_db.add_user(new_user)
#     @intent("Authenticate a user and create a session")
#     @invariant("Failed login attempts must be tracked")
#     @invariant("Accounts should be locked after too many failed attempts")
#     @invariant("Failed login attempts must be tracked")
#     @invariant("Accounts should be locked after too many failed attempts")
    def login(self, username, password):
        """Login a user and return a session token."""
        user = self.user_db.get_user(username)
        
        if not user:
            return None
            
        if user.locked:
            return None
            
        # Bug 4: Timing attack vulnerability (constant-time comparison not used)
        password_hash = hashlib.md5(password.encode()).hexdigest()
        if password_hash != user.password_hash:
            user.login_attempts += 1
            
            # Bug 5: Account locking check happens after the update
            self.user_db.update_user(user)
            
            if user.login_attempts >= self.max_login_attempts:
                user.locked = True
                self.user_db.update_user(user)
                
            return None
        
        # Bug 6: Doesn't reset login attempts after successful login
        
        # Generate session token
        # Bug 7: Weak session token generation
        session_token = str(random.randint(10000, 99999))
        
        self.sessions[session_token] = {
            "username": username,
            "created": time.time()
        }
        
#     @intent("Validate an active session")
#     @invariant("Session tokens must be valid")
#     @invariant("Sessions must not be expired")
#     @invariant("Session tokens must be valid")
#     @invariant("Sessions must not be expired")
    def validate_session(self, session_token):
        """Validate a session token."""
        if session_token not in self.sessions:
            return None
            
        session = self.sessions[session_token]
        
        # Bug 8: No session expiry check
        
        return self.user_db.get_user(session["username"])
        
#     @intent("End a user session")
    def logout(self, session_token):
        """Logout a user by invalidating their session."""
        # Bug 9: Doesn't check if session exists before removing
        del self.sessions[session_token]
        return True
#     @intent("Initiate a password reset process")
#     @invariant("Reset tokens must be secure and time-limited")
#     @invariant("Reset tokens must be secure and time-limited")
    def reset_password(self, username):
        """Generate a password reset token."""
        user = self.user_db.get_user(username)
        
        if not user:
            return None
            
        # Bug 10: Weak reset token
        reset_token = str(random.randint(1000, 9999))
        
        user.reset_token = reset_token
        user.reset_expiry = time.time() + 3600  # 1 hour expiry
        
        self.user_db.update_user(user)
        
#     @intent("Complete a password reset with a valid token")
#     @invariant("Reset token must be valid and not expired")
#     @invariant("New password must meet security requirements")
#     @invariant("Reset token must be valid and not expired")
#     @invariant("New password must meet security requirements")
    def complete_reset(self, username, token, new_password):
        """Complete the password reset process."""
        user = self.user_db.get_user(username)
        
        if not user or not user.reset_token:
            return False
            
        # Bug 11: Token comparison vulnerability
        if token != user.reset_token:
            return False
            
        # Bug 12: Doesn't check token expiry
        
        # Bug 13: Weak hash function again
        user.password_hash = hashlib.md5(new_password.encode()).hexdigest()
        user.reset_token = None
        user.reset_expiry = None
        user.locked = False
        user.login_attempts = 0
        
        self.user_db.update_user(user)
        
        return True
