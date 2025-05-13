from concept_python import intent, invariant, human_decision, ai_implement


class ServiceNotFoundError(Exception):
    pass


class ServiceLocator:
    """COP Annotations:
@intent("Centralize service instantiation and discovery")"""
    _services = {}

    @classmethod
    def register(cls, name, service):
        """COP Annotations:
@intent("Register a service for later retrieval")
@invariant("Service name must be unique")"""
        cls._services[name] = service

    @classmethod
    def get(cls, name):
        """COP Annotations:
@intent("Retrieve a previously registered service")
@invariant("Requested service must exist")"""
        service = cls._services.get(name)
        if not service:
            raise ServiceNotFoundError(f"Service '{name}' not registered")
        return service


class EmailService:
    """COP Annotations:
@intent("Handle email communication")"""

    def send_email(self, to, subject, body):
        """COP Annotations:
@intent("Send an email to a recipient")
@invariant("Recipient, subject, and body must be provided")"""
        print(f'Sending email to {to}: {subject}')
        return True


class NotificationService:
    """COP Annotations:
@intent("Manage user notifications across different channels")"""

    def __init__(self):
        """COP Annotations:
@intent("Initialize with required dependencies")"""
        self.email_service = ServiceLocator.get('email')

    def notify_user(self, user_id, message):
        """COP Annotations:
@intent("Send a notification to a specific user")
@invariant("User ID and message must be valid")"""
        user = self._get_user_email(user_id)
        return self.email_service.send_email(user, 'Notification', message)

    def _get_user_email(self, user_id):
        """COP Annotations:
@intent("Retrieve user email from user ID")
@ai_implement("Implement user email lookup", constraints=["Must handle non-existent users", "Should cache results when appropriate"])"""
        return f'user{user_id}@example.com'


class UserRegistrationService:
    """COP Annotations:
@intent("Handle user registration process")"""

    def __init__(self):
        """COP Annotations:
@intent("Initialize with required dependencies")"""
        self.notification = ServiceLocator.get('notification')

    def register_user(self, name, email):
        """COP Annotations:
@intent("Register a new user in the system")
@invariant("User must have a name and valid email")
@human_decision("Define user registration business rules", roles=["Product Manager", "Security Officer"])"""
        user_id = 123
        self.notification.notify_user(user_id, f'Welcome, {name}!')
        return user_id


def bootstrap_services():
    """COP Annotations:
@intent("Configure application services and dependencies")"""
    email_service = EmailService()
    ServiceLocator.register('email', email_service)
    notification_service = NotificationService()
    ServiceLocator.register('notification', notification_service)
    registration_service = UserRegistrationService()
    ServiceLocator.register('registration', registration_service)


bootstrap_services()
