import json
from django_celery_beat.models import PeriodicTask, IntervalSchedule
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from celery import shared_task
from .models import *


@shared_task(name="Email On Transaction")
def send_transaction_mail(wallet_id, transaction_type, amount):
    # debugging
    print(f":=> Sending transaction! Wallet ID: {wallet_id}")

    try:
        wallet = Wallet.objects.get(id=wallet_id)
        user_email = wallet.user.email
        subject = f"{transaction_type.capitalize()} Confirmation"
        body = f"You have successfully made a {transaction_type} of ${amount}."

        # debugging
        send_mail(
            subject,
            body,
            settings.EMAIL_HOST_USER,
            [user_email],
        )

    except Wallet.DoesNotExist:
        print(f"Error: Wallet with ID {wallet_id} does not exist.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    return wallet_id


@shared_task(name="Balance Report")
def send_balance_report(email, balance):
    subject = "Wallet Balance Report"
    body = f"Your wallet balance is {balance}. \n- Please keep wallet balance minimum 100. \n- Your wallet will be closed after 5 minutes."

    send_mail(
        subject,
        body,
        settings.EMAIL_HOST_USER,
        [email],
    )

    eta_time = timezone.now() + timedelta(minutes=5)
    close_wallet.apply_async(eta=eta_time)


@shared_task(name="Close Wallet")
def close_wallet():
    deleted, _ = Wallet.objects.filter(balance__lt=100).delete()
    if deleted == 0:
        print("No wallets need to be closed.")
    else:
        print(f"{deleted} wallets closed.")

    return True


@shared_task(name="Daily Transaction Report")
def send_transaction_report():
    users = User.objects.all()
    today = timezone.localtime(timezone.now()).date()

    for user in users:
        try:
            # Check if the user has a wallet
            wallet = Wallet.objects.get(user=user)

            # Filter transactions for today's date for this user's wallet
            todays_transactions = wallet.transactions.filter(timestamp__date=today)

            if todays_transactions.exists():
                # Build the email body
                body = f"Dear {user.username},\n\nHere are your transactions for {today}:\n\n"
                for transaction in todays_transactions:
                    body += f"- {transaction.transaction_type.capitalize()} of {transaction.amount} on {transaction.timestamp}\n"

                # Send the email
                send_mail(
                    subject="Daily Transaction Report",
                    message=body,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[user.email],
                    fail_silently=False,  # Set to True if you want to avoid exceptions
                )

                print(f"Email sent to {user.username} for today's transactions.")
            else:
                print(f"No transactions for {user.username} today.")

        except Wallet.DoesNotExist:
            print(f"User {user.username} does not have a wallet.")
            continue


# @shared_task(name="Unsettled Transaction")
# def send_unsettled_transactions():
#     wallets = Wallet.objects.filter(balance__lt=0)
#     today = timezone.now().data()
#     subject = "Unpaid Transactions"
#     body = f"Your unpaid transactions for {today}:\n\n"

#     for wallet in wallets:
#         pass


# @shared_task(name="Zero Balance in Wallet")
# def send_empty_balance_mail():
#     wallets = Wallet.objects.filter(balance__lt=0)
#     today = timezone.now().data()

#     subject = "Zero Balance in Wallet"
#     body = f"Your correspondent balance for {today}:\n\n"
