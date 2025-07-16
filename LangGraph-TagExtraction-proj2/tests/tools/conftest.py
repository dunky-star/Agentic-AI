import pytest
from code.tools.bank_account import BankAccount


@pytest.fixture
def sample_account():
    return BankAccount(100)

@pytest.fixture
def two_accounts():
    return BankAccount(100), BankAccount(50)

