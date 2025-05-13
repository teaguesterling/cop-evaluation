# test_cases/dependencies/service_locator/base.py
class ServiceNotFoundError(Exception):
    pass

class ServiceLocator:
    _services = {}
    
    @classmethod
    def register(cls, name, service):
        cls._services[name] = service
        
    @classmethod
    def get(cls, name):
        service = cls._services.get(name)
        if not service:
            raise ServiceNotFoundError(f"Service '{name}' not registered")
        return service

class EmailService:
    def send_email(self, to, subject, body):
        print(f"Sending email to {to}: {subject}")
        return True

class NotificationService:
    def __init__(self):
        self.email_service = ServiceLocator.get("email")
    
    def notify_user(self, user_id, message):
        user = self._get_user_email(user_id)
        return self.email_service.send_email(user, "Notification", message)
        
    def _get_user_email(self, user_id):
        # In a real app, would fetch from database
        return f"user{user_id}@example.com"

class UserRegistrationService:
    def __init__(self):
        self.notification = ServiceLocator.get("notification")
    
    def register_user(self, name, email):
        # Register user logic
        user_id = 123  # Would be dynamic in real app
        self.notification.notify_user(user_id, f"Welcome, {name}!")
        return user_id

# Application bootstrap
email_service = EmailService()
ServiceLocator.register("email", email_service)

notification_service = NotificationService()
ServiceLocator.register("notification", notification_service)

registration_service = UserRegistrationService()
ServiceLocator.register("registration", registration_service)
