from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "username",
            "password",
            "email",
        ]
        extra_kwargs = {
            "password": {
                "write_only": True,
            },
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class WalletSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = Wallet
        fields = ["id", "user", "name", "balance", "currency"]


class TransactionSerializer(serializers.ModelSerializer):
    wallet = serializers.PrimaryKeyRelatedField(queryset=Wallet.objects.all())
    recipient_wallet = serializers.PrimaryKeyRelatedField(
        queryset=Wallet.objects.all(), required=False, allow_null=True
    )

    class Meta:
        model = Transaction
        fields = [
            "id",
            "wallet",
            "transaction_type",
            "amount",
            "timestamp",
            "recipient_wallet",
        ]

    def validate(self, data):
        user = self.context["request"].user
        wallet = data.get("wallet")

        if wallet and wallet.user != user:
            raise serializers.ValidationError(
                {"authError": "You do not own this wallet."}
            )

        recipient_wallet = data.get("recipient_wallet")
        if recipient_wallet and recipient_wallet.user == user:
            raise serializers.ValidationError(
                {"authError": "Cannot send to your own wallet."}
            )
        return data


class SettlementSerializer(serializers.ModelSerializer):
    transaction = serializers.PrimaryKeyRelatedField(queryset=Transaction.objects.all())

    class Meta:
        model = Settlement
        fields = ["id", "transaction", "settled", "settlement_date"]
