from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


# Wallet Model to store user's balance
class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    currency = models.CharField(max_length=3, default="USD")  # e.g. USD, EUR

    def __str__(self):
        return (
            f"{self.user.username}'s wallet - Balance: {self.balance} {self.currency}"
        )

    def deposit(self, amount):
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
        self.save()

    def withdraw(self, amount):
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if self.balance < amount:
            raise ValueError("Insufficient funds")
        self.balance -= amount
        self.save()


# Transaction Model to track the movement of money
class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ("deposit", "Deposit"),
        ("withdraw", "Withdraw"),
        ("transfer", "Transfer"),
        ("settlement", "Settlement"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    wallet = models.ForeignKey(
        Wallet, on_delete=models.CASCADE, related_name="transactions"
    )
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now)
    recipient_wallet = models.ForeignKey(
        Wallet,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="incoming_transactions",
    )  # Only for transfer/settlement

    def __str__(self):
        return (
            f"{self.transaction_type.capitalize()} of {self.amount} on {self.timestamp}"
        )


# Settlement Model to represent settling a payment after a transaction
class Settlement(models.Model):
    transaction = models.OneToOneField(Transaction, on_delete=models.CASCADE)
    settled = models.BooleanField(default=False)
    settlement_date = models.DateTimeField(null=True, blank=True)

    def mark_as_settled(self):
        self.settled = True
        self.settlement_date = timezone.now()
        self.save()

    def __str__(self):
        return f"Settlement for {self.transaction.id} - Settled: {self.settled}"
