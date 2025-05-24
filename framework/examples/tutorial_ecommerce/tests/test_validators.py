import unittest
from decimal import Decimal
import sys
sys.path.append('/mnt/aux-data/teague/Projects/MindMeld/cop-testing/framework')
from cop_python.testing.annotations import test_for, test_invariant, test_risk

# Import validators
sys.path.append('/mnt/aux-data/teague/Projects/MindMeld/cop-testing/framework/examples/tutorial_ecommerce')
from src.utils.validators import (
    EmailValidator, PhoneValidator, CurrencyValidator, 
    AddressValidator, PasswordValidator
)


class TestEmailValidator(unittest.TestCase):

    @test_for("utils.validators.EmailValidator.is_valid_email")
    @test_invariant("email is not None")
    @test_risk("LOW", component="utils.validators.EmailValidator.is_valid_email")
    def test_valid_email_addresses(self):
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "first.last+tag@example.org",
            "user123@test-domain.com"
        ]
        
        for email in valid_emails:
            with self.subTest(email=email):
                self.assertTrue(EmailValidator.is_valid_email(email))

    @test_for("utils.validators.EmailValidator.is_valid_email")
    def test_invalid_email_addresses(self):
        invalid_emails = [
            "",
            "notanemail",
            "@example.com",
            "user@",
            "user..name@example.com",
            "user@.com"
        ]
        
        for email in invalid_emails:
            with self.subTest(email=email):
                self.assertFalse(EmailValidator.is_valid_email(email))

    @test_for("utils.validators.EmailValidator.get_email_domain")
    @test_invariant("email contains @")
    def test_extract_email_domain(self):
        self.assertEqual(EmailValidator.get_email_domain("test@example.com"), "example.com")
        self.assertEqual(EmailValidator.get_email_domain("user@domain.co.uk"), "domain.co.uk")
        self.assertIsNone(EmailValidator.get_email_domain("invalid-email"))


class TestPhoneValidator(unittest.TestCase):

    @test_for("utils.validators.PhoneValidator.is_valid_us_phone")
    @test_invariant("phone is not None")
    def test_valid_us_phone_numbers(self):
        valid_phones = [
            "1234567890",
            "11234567890",
            "(123) 456-7890",
            "123-456-7890",
            "+1 123 456 7890"
        ]
        
        for phone in valid_phones:
            with self.subTest(phone=phone):
                self.assertTrue(PhoneValidator.is_valid_us_phone(phone))

    @test_for("utils.validators.PhoneValidator.is_valid_us_phone")
    def test_invalid_us_phone_numbers(self):
        invalid_phones = [
            "",
            "123",
            "12345678901234",  # Too long
            "abcd567890"
        ]
        
        for phone in invalid_phones:
            with self.subTest(phone=phone):
                self.assertFalse(PhoneValidator.is_valid_us_phone(phone))

    @test_for("utils.validators.PhoneValidator.format_us_phone")
    @test_invariant("phone is valid US phone number")
    def test_format_us_phone(self):
        self.assertEqual(PhoneValidator.format_us_phone("1234567890"), "(123) 456-7890")
        self.assertEqual(PhoneValidator.format_us_phone("11234567890"), "(123) 456-7890")
        self.assertIsNone(PhoneValidator.format_us_phone("invalid"))


class TestCurrencyValidator(unittest.TestCase):

    @test_for("utils.validators.CurrencyValidator.is_valid_currency_amount")
    @test_invariant("amount is not None")
    @test_risk("MEDIUM", component="utils.validators.CurrencyValidator.is_valid_currency_amount")
    def test_valid_currency_amounts(self):
        valid_amounts = [
            Decimal('10.00'),
            Decimal('99.99'),
            Decimal('1000.50'),
            Decimal('0.01')
        ]
        
        for amount in valid_amounts:
            with self.subTest(amount=amount):
                self.assertTrue(CurrencyValidator.is_valid_currency_amount(amount))

    @test_for("utils.validators.CurrencyValidator.is_valid_currency_amount")
    def test_invalid_currency_amounts(self):
        invalid_amounts = [
            Decimal('0'),
            Decimal('-10.00'),
            Decimal('10.999'),  # Too many decimal places
        ]
        
        for amount in invalid_amounts:
            with self.subTest(amount=amount):
                self.assertFalse(CurrencyValidator.is_valid_currency_amount(amount))

    @test_for("utils.validators.CurrencyValidator.round_currency")
    @test_invariant("amount >= 0")
    def test_round_currency(self):
        self.assertEqual(CurrencyValidator.round_currency(Decimal('10.999')), Decimal('11.00'))
        self.assertEqual(CurrencyValidator.round_currency(Decimal('10.994')), Decimal('10.99'))
        self.assertEqual(CurrencyValidator.round_currency(Decimal('10.00')), Decimal('10.00'))

    @test_for("utils.validators.CurrencyValidator.format_currency")
    @test_invariant("amount >= 0")
    def test_format_currency(self):
        self.assertEqual(CurrencyValidator.format_currency(Decimal('1234.56')), "$1,234.56")
        self.assertEqual(CurrencyValidator.format_currency(Decimal('10.00')), "$10.00")
        self.assertEqual(CurrencyValidator.format_currency(Decimal('0.99')), "$0.99")


class TestAddressValidator(unittest.TestCase):

    @test_for("utils.validators.AddressValidator.is_valid_us_zip")
    @test_invariant("zip_code is not None")
    def test_valid_us_zip_codes(self):
        valid_zips = [
            "12345",
            "12345-6789",
            "12345 6789",
            "123456789"
        ]
        
        for zip_code in valid_zips:
            with self.subTest(zip_code=zip_code):
                self.assertTrue(AddressValidator.is_valid_us_zip(zip_code))

    @test_for("utils.validators.AddressValidator.is_valid_us_zip")
    def test_invalid_us_zip_codes(self):
        invalid_zips = [
            "",
            "1234",
            "123456",
            "abcde",
            "12345-67890"  # Too long
        ]
        
        for zip_code in invalid_zips:
            with self.subTest(zip_code=zip_code):
                self.assertFalse(AddressValidator.is_valid_us_zip(zip_code))

    @test_for("utils.validators.AddressValidator.is_valid_us_state")
    @test_invariant("state is not None")
    def test_valid_us_states(self):
        valid_states = ["CA", "NY", "TX", "FL", "ca", "ny"]  # Should handle case
        
        for state in valid_states:
            with self.subTest(state=state):
                self.assertTrue(AddressValidator.is_valid_us_state(state))

    @test_for("utils.validators.AddressValidator.is_valid_us_state")
    def test_invalid_us_states(self):
        invalid_states = ["", "XY", "ABC", "California"]
        
        for state in invalid_states:
            with self.subTest(state=state):
                self.assertFalse(AddressValidator.is_valid_us_state(state))

    @test_for("utils.validators.AddressValidator.is_valid_us_address")
    @test_invariant("address components are not None")
    @test_risk("LOW", component="utils.validators.AddressValidator.is_valid_us_address")
    def test_valid_us_address(self):
        self.assertTrue(AddressValidator.is_valid_us_address(
            "123 Main Street", "Anytown", "CA", "12345"
        ))

    @test_for("utils.validators.AddressValidator.is_valid_us_address")
    def test_invalid_us_address(self):
        # Invalid street (too short)
        self.assertFalse(AddressValidator.is_valid_us_address(
            "123", "Anytown", "CA", "12345"
        ))
        
        # Invalid state
        self.assertFalse(AddressValidator.is_valid_us_address(
            "123 Main Street", "Anytown", "XY", "12345"
        ))
        
        # Invalid ZIP
        self.assertFalse(AddressValidator.is_valid_us_address(
            "123 Main Street", "Anytown", "CA", "123"
        ))


class TestPasswordValidator(unittest.TestCase):

    @test_for("utils.validators.PasswordValidator.is_strong_password")
    @test_invariant("password is not None")
    @test_risk("HIGH", component="utils.validators.PasswordValidator.is_strong_password")
    def test_strong_passwords(self):
        strong_passwords = [
            "Password123!",
            "MyStr0ng@Pass",
            "C0mpl3x#P@ssw0rd",
            "Secur3!Password"
        ]
        
        for password in strong_passwords:
            with self.subTest(password=password):
                self.assertTrue(PasswordValidator.is_strong_password(password))

    @test_for("utils.validators.PasswordValidator.is_strong_password")
    def test_weak_passwords(self):
        weak_passwords = [
            "",
            "password",      # No uppercase, digits, special chars
            "PASSWORD",      # No lowercase, digits, special chars
            "Password",      # No digits, special chars
            "Password1",     # No special chars
            "Pass1!",        # Too short
        ]
        
        for password in weak_passwords:
            with self.subTest(password=password):
                self.assertFalse(PasswordValidator.is_strong_password(password))

    @test_for("utils.validators.PasswordValidator.calculate_strength_score")
    @test_invariant("password is not None")
    def test_password_strength_scores(self):
        # Strong password should have high score
        strong_score = PasswordValidator.calculate_strength_score("MyStr0ng@Password123")
        self.assertGreater(strong_score, 50)
        
        # Weak password should have low score
        weak_score = PasswordValidator.calculate_strength_score("password")
        self.assertLess(weak_score, 30)
        
        # Empty password should have zero score
        empty_score = PasswordValidator.calculate_strength_score("")
        self.assertEqual(empty_score, 0)


if __name__ == '__main__':
    unittest.main()