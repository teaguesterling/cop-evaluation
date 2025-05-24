from typing import Optional, List
from decimal import Decimal
from dataclasses import dataclass
from datetime import datetime
import sys
sys.path.append('/mnt/aux-data/teague/Projects/MindMeld/cop-testing/framework')
from cop_python.annotations import intent, invariant, risk, implementation_status, decision


@dataclass
class Address:
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "US"

    @intent("Validate address format for shipping calculations")
    @invariant("len(zip_code) in [5, 9] and state.isupper() and len(state) == 2")
    @implementation_status("IMPLEMENTED")
    def is_valid(self) -> bool:
        return (
            len(self.zip_code) in [5, 9] and
            self.state.isupper() and
            len(self.state) == 2 and
            len(self.street.strip()) > 0 and
            len(self.city.strip()) > 0
        )


@dataclass  
class User:
    user_id: str
    email: str
    first_name: str
    last_name: str
    credit_limit: Decimal
    current_balance: Decimal
    addresses: List[Address]
    created_at: datetime
    is_premium: bool = False

    @intent("Calculate available credit for order validation")
    @invariant("available_credit >= 0 and available_credit <= credit_limit")
    @implementation_status("IMPLEMENTED")
    def get_available_credit(self) -> Decimal:
        return max(Decimal('0'), self.credit_limit - self.current_balance)

    @intent("Validate user can afford the specified order amount")
    @invariant("amount > 0")
    @risk("MEDIUM", details="Credit decisions impact business revenue and customer satisfaction")
    @implementation_status("IMPLEMENTED")
    def can_afford(self, amount: Decimal) -> bool:
        if amount <= 0:
            return False
        return self.get_available_credit() >= amount

    @intent("Get primary shipping address for order processing")
    @decision("Use first address as primary", alternatives=["Separate primary flag", "Most recent address"])
    @implementation_status("IMPLEMENTED")
    def get_primary_address(self) -> Optional[Address]:
        return self.addresses[0] if self.addresses else None

    @intent("Update user balance after successful payment")
    @invariant("amount > 0 and self.current_balance + amount <= self.credit_limit")
    @risk("HIGH", details="Balance updates affect credit calculations and financial records")
    @implementation_status("IMPLEMENTED")
    def charge_account(self, amount: Decimal) -> bool:
        if amount <= 0 or not self.can_afford(amount):
            return False
        self.current_balance += amount
        return True