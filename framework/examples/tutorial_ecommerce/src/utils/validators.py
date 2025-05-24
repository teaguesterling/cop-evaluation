import re
from typing import Optional
from decimal import Decimal
import sys
sys.path.append('/mnt/aux-data/teague/Projects/MindMeld/cop-testing/framework')
from cop_python.annotations import intent, invariant, risk, implementation_status, decision


class EmailValidator:
    @staticmethod
    @intent("Validate email address format")
    @invariant("email is not None")
    @risk("LOW", details="Email validation affects user registration and communications")
    @decision("Regex-based validation", alternatives=["Third-party service", "DNS verification"])
    @implementation_status("IMPLEMENTED")
    def is_valid_email(email: str) -> bool:
        if not email:
            return False
            
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    @staticmethod
    @intent("Extract domain from email address")
    @invariant("email contains @")
    @implementation_status("IMPLEMENTED")
    def get_email_domain(email: str) -> Optional[str]:
        if not EmailValidator.is_valid_email(email):
            return None
        return email.split('@')[1]


class PhoneValidator:
    @staticmethod
    @intent("Validate US phone number format")
    @invariant("phone is not None")
    @implementation_status("IMPLEMENTED")
    def is_valid_us_phone(phone: str) -> bool:
        if not phone:
            return False
            
        # Remove all non-digits
        digits = re.sub(r'\D', '', phone)
        
        # Should be 10 digits (US) or 11 digits (US with country code)
        return len(digits) in [10, 11] and (len(digits) == 10 or digits.startswith('1'))

    @staticmethod
    @intent("Format phone number for display")
    @invariant("phone is valid US phone number")
    @implementation_status("IMPLEMENTED")
    def format_us_phone(phone: str) -> Optional[str]:
        if not PhoneValidator.is_valid_us_phone(phone):
            return None
            
        digits = re.sub(r'\D', '', phone)
        
        if len(digits) == 11 and digits.startswith('1'):
            digits = digits[1:]  # Remove country code
            
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"


class CurrencyValidator:
    @staticmethod
    @intent("Validate currency amount is positive and has appropriate precision")
    @invariant("amount is not None")
    @risk("MEDIUM", details="Currency validation prevents financial calculation errors")
    @implementation_status("IMPLEMENTED")
    def is_valid_currency_amount(amount: Decimal) -> bool:
        if amount is None:
            return False
            
        # Must be positive
        if amount <= 0:
            return False
            
        # Check precision (max 2 decimal places for currency)
        return amount.as_tuple().exponent >= -2

    @staticmethod
    @intent("Round currency amount to appropriate precision")
    @invariant("amount >= 0")
    @implementation_status("IMPLEMENTED")
    def round_currency(amount: Decimal) -> Decimal:
        return amount.quantize(Decimal('0.01'))

    @staticmethod
    @intent("Format currency amount for display")
    @invariant("amount >= 0")
    @implementation_status("IMPLEMENTED")
    def format_currency(amount: Decimal, currency_symbol: str = "$") -> str:
        rounded = CurrencyValidator.round_currency(amount)
        return f"{currency_symbol}{rounded:,.2f}"


class AddressValidator:
    US_STATES = {
        'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
        'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
        'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
        'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
        'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
    }

    @staticmethod
    @intent("Validate US ZIP code format")
    @invariant("zip_code is not None")
    @implementation_status("IMPLEMENTED")
    def is_valid_us_zip(zip_code: str) -> bool:
        if not zip_code:
            return False
            
        # Remove spaces and hyphens
        cleaned = re.sub(r'[\s-]', '', zip_code)
        
        # Should be 5 digits or 9 digits (ZIP+4)
        return bool(re.match(r'^\d{5}(\d{4})?$', cleaned))

    @staticmethod
    @intent("Validate US state abbreviation")
    @invariant("state is not None")
    @implementation_status("IMPLEMENTED")
    def is_valid_us_state(state: str) -> bool:
        if not state:
            return False
        return state.upper() in AddressValidator.US_STATES

    @staticmethod
    @intent("Validate complete US address")
    @invariant("address components are not None")
    @risk("LOW", details="Address validation affects shipping calculations and delivery")
    @implementation_status("IMPLEMENTED")
    def is_valid_us_address(street: str, city: str, state: str, zip_code: str) -> bool:
        if not all([street, city, state, zip_code]):
            return False
            
        # Basic length checks
        if len(street.strip()) < 5 or len(city.strip()) < 2:
            return False
            
        return (AddressValidator.is_valid_us_state(state) and 
                AddressValidator.is_valid_us_zip(zip_code))


class PasswordValidator:
    @staticmethod
    @intent("Validate password meets security requirements")
    @invariant("password is not None")
    @risk("HIGH", details="Password validation is critical for account security")
    @decision("Rules-based validation", alternatives=["Entropy-based", "Dictionary check"])
    @implementation_status("IMPLEMENTED")
    def is_strong_password(password: str) -> bool:
        if not password:
            return False
            
        # Minimum length
        if len(password) < 8:
            return False
            
        # Must contain at least one of each: uppercase, lowercase, digit, special char
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        
        return all([has_upper, has_lower, has_digit, has_special])

    @staticmethod
    @intent("Calculate password strength score")
    @invariant("password is not None")
    @implementation_status("IMPLEMENTED")
    def calculate_strength_score(password: str) -> int:
        if not password:
            return 0
            
        score = 0
        
        # Length bonus
        score += min(len(password), 20)
        
        # Character type bonuses
        if re.search(r'[a-z]', password):
            score += 5
        if re.search(r'[A-Z]', password):
            score += 5
        if re.search(r'\d', password):
            score += 5
        if re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            score += 10
            
        # Penalty for common patterns
        if re.search(r'(.)\1{2,}', password):  # Repeated characters
            score -= 10
        if re.search(r'(012|123|234|345|456|567|678|789|890)', password):  # Sequential numbers
            score -= 5
            
        return max(0, min(score, 100))  # Clamp between 0-100