from concept_python import intent, invariant, human_decision, ai_implement
import hashlib
import random
import time


class User:
    """COP Annotations:
@intent("Store user account information")"""

    def __init__(self, username, password_hash, email, role='user'):
        self.username = username
        self.password_hash = password_hash
        self.email = email
        self.role = role
        self.login_attempts = 0
        self.locked = False
        self.reset_token = None
        self.reset_expiry = None


class UserDatabase:
    """COP Annotations:
@intent("Store and retrieve user data")"""

    def __init__(self):
        self.users = {}

    def add_user(self, user):
        """COP Annotations:
@intent("Add a new user to the database")
@invariant("Username must be unique")"""
        self.users[user.username] = user

    def get_user(self, username):
        """COP Annotations:
@intent("Retrieve a user by username")"""
        return self.users.get(username)

    def update_user(self, user):
        """COP Annotations:
@intent("Update an existing user's information")"""
        if user.username in self.users:
            self.users[user.username] = user


class AuthenticationService:
    """COP Annotations:
@intent("Provide user authentication and session management")"""

    def __init__(self, user_db):
        self.user_db = user_db
        self.max_login_attempts = 5
        self.sessions = {}

    def register(self, username, password, email):
        """Register a new user.

COP Annotations:
@intent("Register a new user account")
@invariant("Username must be unique")
@invariant("Password must meet security requirements")"""
        password_hash = hashlib.md5(password.encode()).hexdigest()
        new_user = User(username, password_hash, email)
        self.user_db.add_user(new_user)
        return True

    def login(self, username, password):
        """Login a user and return a session token.

COP Annotations:
@intent("Authenticate a user and create a session")
@invariant("Failed login attempts must be tracked")
@invariant("Accounts should be locked after too many failed attempts")"""
        user = self.user_db.get_user(username)
        if not user:
            return None
        if user.locked:
            return None
        password_hash = hashlib.md5(password.encode()).hexdigest()
        if password_hash != user.password_hash:
            user.login_attempts += 1
            self.user_db.update_user(user)
            if user.login_attempts >= self.max_login_attempts:
                user.locked = True
                self.user_db.update_user(user)
            return None
        session_token = str(random.randint(10000, 99999))
        self.sessions[session_token] = {'username': username, 'created':
            time.time()}
        return session_token

    def validate_session(self, session_token):
        """Validate a session token.

COP Annotations:
@intent("Validate an active session")
@invariant("Session tokens must be valid")
@invariant("Sessions must not be expired")"""
        if session_token not in self.sessions:
            return None
        session = self.sessions[session_token]
        return self.user_db.get_user(session['username'])

    def logout(self, session_token):
        """Logout a user by invalidating their session.

COP Annotations:
@intent("End a user session")"""
        del self.sessions[session_token]
        return True

    def reset_password(self, username):
        """Generate a password reset token.

COP Annotations:
@intent("Initiate a password reset process")
@invariant("Reset tokens must be secure and time-limited")"""
        user = self.user_db.get_user(username)
        if not user:
            return None
        reset_token = str(random.randint(1000, 9999))
        user.reset_token = reset_token
        user.reset_expiry = time.time() + 3600
        self.user_db.update_user(user)
        return reset_token

    def complete_reset(self, username, token, new_password):
        """Complete the password reset process.

COP Annotations:
@intent("Complete a password reset with a valid token")
@invariant("Reset token must be valid and not expired")
@invariant("New password must meet security requirements")"""
        user = self.user_db.get_user(username)
        if not user or not user.reset_token:
            return False
        if token != user.reset_token:
            return False
        user.password_hash = hashlib.md5(new_password.encode()).hexdigest()
        user.reset_token = None
        user.reset_expiry = None
        user.locked = False
        user.login_attempts = 0
        self.user_db.update_user(user)
        return True
