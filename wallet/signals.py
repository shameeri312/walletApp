from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.utils import timezone
from .models import *
from .tasks import *


@receiver(post_save, sender=User)
def create_wallet(sender, instance, created, **kwargs):
    if created:
        Wallet.objects.create(user=instance)


@receiver(post_save, sender=Transaction)
def update_wallet_balance(sender, instance, created, **kwargs):
    if created:
        if instance.transaction_type == "deposit":
            instance.wallet.balance += instance.amount
        elif instance.transaction_type == "withdraw":
            if instance.wallet.balance >= instance.amount:
                instance.wallet.balance -= instance.amount
                # ----------------------------------------
                if instance.wallet.balance <= 0:
                    # Send email to the sender
                    eta_time = timezone.now() + timezone.timedelta(seconds=10)
                    send_balance_report.apply_async(
                        args=[instance.wallet.user.email, instance.wallet.balance],
                        eta=eta_time,
                    )
            else:
                raise ValueError("Insufficient balance for withdrawal")
        elif instance.transaction_type == "transfer" and instance.recipient_wallet:
            # Deduct from sender's wallet
            if instance.wallet.balance >= instance.amount:
                instance.wallet.balance -= instance.amount
                # ----------------------------------------
                if instance.wallet.balance <= 0:
                    # Send email to the sender
                    eta_time = timezone.now() + timezone.timedelta(seconds=10)
                    send_balance_report.apply_async(
                        args=[instance.wallet.user.email, instance.wallet.balance],
                        eta=eta_time,
                    )
                # Add to recipient's wallet
                instance.recipient_wallet.balance += instance.amount
            else:
                raise ValueError("Insufficient balance for transfer")

        # Save the updated wallet balances
        instance.wallet.save()

        if instance.recipient_wallet:
            instance.recipient_wallet.save()

        if instance.transaction_type in ["transfer", "settlement"]:
            # Create a new settlement instance
            Settlement.objects.create(transaction=instance)
