# test_cases/dependencies/service_locator/cop.py
from cop_python import intent, invariant, human_decision, ai_implement

class ServiceNotFoundError(Exception):
    pass

@intent("Centralize service instantiation and discovery")
class ServiceLocator:
    _services = {}
    
    @classmethod
    @intent("Register a service for later retrieval")
    @invariant("Service name must be unique")
    def register(cls, name, service):
        cls._services[name] = service
        
    @classmethod
    @intent("Retrieve a previously registered service")
    @invariant("Requested service must exist")
    def get(cls, name):
        service = cls._services.get(name)
        if not service:
            raise ServiceNotFoundError(f"Service '{name}' not registered")
        return service

@intent("Handle email communication")
class EmailService:
    @intent("Send an email to a recipient")
    @invariant("Recipient, subject, and body must be provided")
    def send_email(self, to, subject, body):
        print(f"Sending email to {to}: {subject}")
        return True

@intent("Manage user notifications across different channels")
class NotificationService:
    @intent("Initialize with required dependencies")
    def __init__(self):
        self.email_service = ServiceLocator.get("email")
    
    @intent("Send a notification to a specific user")
    @invariant("User ID and message must be valid")
    def notify_user(self, user_id, message):
        user = self._get_user_email(user_id)
        return self.email_service.send_email(user, "Notification", message)
        
    @intent("Retrieve user email from user ID")
    @ai_implement("Implement user email lookup",
                 constraints=["Must handle non-existent users",
                             "Should cache results when appropriate"])
    def _get_user_email(self, user_id):
        # In a real app, would fetch from database
        return f"user{user_id}@example.com"

@intent("Handle user registration process")
class UserRegistrationService:
    @intent("Initialize with required dependencies")
    def __init__(self):
        self.notification = ServiceLocator.get("notification")
    
    @intent("Register a new user in the system")
    @invariant("User must have a name and valid email")
    @human_decision("Define user registration business rules",
                   roles=["Product Manager", "Security Officer"])
    def register_user(self, name, email):
        # Register user logic
        user_id = 123  # Would be dynamic in real app
        self.notification.notify_user(user_id, f"Welcome, {name}!")
        return user_id

# Application bootstrap - service configuration
@intent("Configure application services and dependencies")
def bootstrap_services():
    email_service = EmailService()
    ServiceLocator.register("email", email_service)
    
    notification_service = NotificationService()
    ServiceLocator.register("notification", notification_service)
    
    registration_service = UserRegistrationService()
    ServiceLocator.register("registration", registration_service)

bootstrap_services()
