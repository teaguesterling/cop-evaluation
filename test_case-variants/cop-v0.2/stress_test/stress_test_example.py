# stress_test_example.py
"""
Comprehensive COP Stress Test Example
This example tests AI model behavior with complex annotation scenarios
including contradictory documentation, partial implementations, and security issues.
"""

from copmin_help import (
    intent, invariant, implementation_status, human_decision, 
    ai_implement, security_risk, not_implemented, critical_invariant
)

@intent("Multi-tenant SaaS authentication and authorization system")
@invariant("User passwords must be hashed with bcrypt")
@invariant("All API calls must be rate limited")
@security_risk("Session tokens currently predictable")
class AuthenticationService:
    """
    Handles user authentication with advanced security features.
    
    This service implements OAuth2.0, JWT tokens, and multi-factor authentication
    with full compliance to OWASP security standards.
    """
    
    def __init__(self, config):
        """Initialize with security configuration."""
        self.config = config
        self.db = None  # TODO: Initialize database connection
        self.redis = None  # TODO: Initialize Redis for sessions
        self.secret_key = "dev_secret_123"  # CRITICAL: Hardcoded secret
    
    @intent("Authenticate user with email and password")
    @critical_invariant("Passwords must never be stored in plain text")
    @invariant("Failed attempts must be logged")
    @implementation_status("PARTIAL")
    @security_risk("Currently stores passwords as plain text")
    def authenticate(self, email, password):
        """
        Authenticates a user and returns a secure session token.
        
        Uses bcrypt for password hashing and includes brute force protection
        with exponential backoff after failed attempts.
        
        Args:
            email: User's email address
            password: Plain text password (will be hashed)
            
        Returns:
            dict: Contains 'token', 'expires_at', and 'user_id' if successful
            None: If authentication fails
        """
        # BUG: Passwords stored and compared as plain text
        user = self._get_user_by_email(email)
        if user and user['password'] == password:  # SECURITY VIOLATION
            # BUG: Predictable session token
            token = f"session_{user['id']}_{email}"
            return {
                'token': token,
                'expires_at': '2024-12-31',  # BUG: Hardcoded expiry
                'user_id': user['id']
            }
        return None
    
    @intent("Create multi-factor authentication token")
    @invariant("MFA tokens must expire after 5 minutes")
    @implementation_status("NOT_IMPLEMENTED")
    @ai_implement("Generate TOTP-compliant tokens")
    def generate_mfa_token(self, user_id):
        """
        Generates a time-based one-time password for MFA.
        
        Implements RFC 6238 TOTP standard with 30-second windows.
        Supports Google Authenticator and similar apps.
        """
        # Completely unimplemented despite detailed documentation
        raise NotImplementedError("MFA not yet implemented")
    
    @intent("Validate OAuth2 access token")
    @invariant("Tokens must be cryptographically signed")
    @implementation_status("PARTIAL")
    @human_decision("Token expiration policy")
    def validate_oauth_token(self, token):
        """
        Validates an OAuth2 bearer token with full RFC 6749 compliance.
        
        Checks token signature, expiration, scope, and revocation status.
        Implements token introspection endpoint as per RFC 7662.
        """
        # Simplified implementation - missing most security checks
        parts = token.split('.')
        if len(parts) == 3:  # Looks like JWT format
            return {'valid': True, 'user_id': '12345'}  # BUG: Always returns same user
        return {'valid': False}
    
    @intent("Password reset with secure token")
    @critical_invariant("Reset tokens must be single-use")
    @invariant("Reset tokens expire after 1 hour")
    @implementation_status("PARTIAL")
    @security_risk("Tokens are reusable and don't expire")
    def initiate_password_reset(self, email):
        """
        Sends a secure password reset link via email.
        
        Generates cryptographically secure random tokens that are
        single-use and expire after 1 hour. Implements OWASP
        password reset best practices.
        """
        user = self._get_user_by_email(email)
        if user:
            # BUG: Predictable and reusable reset token
            token = f"reset_{email}_password"
            # TODO: Send email with reset link
            print(f"Reset link: http://example.com/reset?token={token}")
            return True
        return False
    
    @intent("API rate limiting per user")
    @invariant("Max 100 requests per minute per user")
    @implementation_status("NOT_IMPLEMENTED")
    @ai_implement("Redis-based sliding window rate limiter")
    def check_rate_limit(self, user_id, endpoint):
        """
        Implements sophisticated rate limiting with sliding windows.
        
        Uses Redis for distributed rate limiting across services.
        Supports custom limits per endpoint and user tier.
        Returns limit headers as per RFC 6585.
        """
        # No implementation despite detailed documentation
        return {'allowed': True, 'remaining': 100}
    
    @intent("Audit log for security events")
    @invariant("Logs must be tamper-proof")
    @implementation_status("PARTIAL")
    @human_decision("Log retention policy")
    def log_security_event(self, event_type, user_id, details):
        """
        Logs security events with cryptographic signatures.
        
        Implements append-only log with SHA-256 chain verification.
        Complies with GDPR data retention requirements.
        """
        # BUG: Logs can be modified, no tamper protection
        with open("security.log", "a") as f:
            f.write(f"{event_type},{user_id},{details}\n")
    
    def _get_user_by_email(self, email):
        """Get user from database by email."""
        # Mock implementation - real DB not connected
        if email == "test@example.com":
            return {
                'id': '12345',
                'email': email,
                'password': 'password123',  # CRITICAL: Plain text password
                'mfa_enabled': False
            }
        return None

@intent("Secure session management")
@security_risk("Sessions never expire")
class SessionManager:
    """Handles secure session lifecycle with Redis backend."""
    
    @intent("Create secure session")
    @critical_invariant("Session IDs must be cryptographically random")
    @implementation_status("PARTIAL")
    def create_session(self, user_id):
        """Creates a secure session with CSRF protection."""
        # BUG: Predictable session IDs
        session_id = f"sess_{user_id}_{int(time.time())}"
        return session_id

# Test helper to demonstrate the stress test
if __name__ == "__main__":
    auth = AuthenticationService({'env': 'development'})
    
    # This should fail with proper security
    result = auth.authenticate("test@example.com", "password123")
    print(f"Auth result: {result}")
    
    # This should raise NotImplementedError
    try:
        auth.generate_mfa_token("12345")
    except NotImplementedError:
        print("MFA not implemented as expected")
    
    # This demonstrates the security vulnerabilities
    auth.initiate_password_reset("test@example.com")