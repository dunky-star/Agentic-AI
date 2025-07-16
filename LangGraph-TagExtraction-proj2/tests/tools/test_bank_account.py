# test_bank_account.py
import pytest
from code.tools.bank_account import BankAccount

class TestBankAccount:

    def test_initial_balance_default(self):
        """Test account creation with default balance."""
        account = BankAccount()
        assert account.balance == 0

    def test_initial_balance_custom(self):
        """Test account creation with custom balance."""
        account = BankAccount(100)
        assert account.balance == 100

    def test_initial_balance_negative(self):
        """Test that negative initial balance raises error."""
        with pytest.raises(ValueError, match="Initial balance cannot be negative"):
            BankAccount(-50)

    def test_deposit_positive_amount(self):
        """Test depositing positive amount."""
        account = BankAccount(100)
        new_balance = account.deposit(50)
        assert new_balance == 150
        assert account.balance == 150

    def test_deposit_zero_amount(self):
        """Test that depositing zero raises error."""
        account = BankAccount(100)
        with pytest.raises(ValueError, match="Deposit amount must be positive"):
            account.deposit(0)

    def test_withdraw_valid_amount(self):
        """Test withdrawing valid amount."""
        account = BankAccount(100)
        new_balance = account.withdraw(30)
        assert new_balance == 70
        assert account.balance == 70

    def test_withdraw_insufficient_funds(self):
        """Test that withdrawing more than balance raises error."""
        account = BankAccount(50)
        with pytest.raises(ValueError, match="Insufficient funds"):
            account.withdraw(100)

    def test_transfer_between_accounts(self):
        """Test transferring money between accounts."""
        account1 = BankAccount(100)
        account2 = BankAccount(50)

        account1.transfer(30, account2)

        assert account1.balance == 70
        assert account2.balance == 80

    def test_transfer_invalid_target(self):
        """Test that transferring to invalid target raises error."""
        account = BankAccount(100)
        with pytest.raises(TypeError, match="Target must be a BankAccount instance"):
            account.transfer(50, "not_an_account")