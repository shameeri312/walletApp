from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, status
from django.contrib.auth.models import User
from .serializers import *
from .models import *
from .tasks import *


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]


class WalletViewSet(viewsets.ModelViewSet):
    queryset = Wallet.objects.all()
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {"request": self.request}


class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Save the transaction instance
        serializer.save()
        wallet_id = request.data.get("wallet")
        transaction_type = request.data.get("transaction_type")
        amount = request.data.get("amount")

        print("-> Wallet_id:", wallet_id)
        print("-> Transaction_type:", transaction_type)
        print("-> Amount:", amount)

        send_transaction_mail.delay(wallet_id, transaction_type, amount)
        # send_transaction_mail.apply_async(args=([wallet_id, transaction_type, amount]))

        # You can customize the response here if needed
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def get_serializer_context(self):
        return {"request": self.request}


class SettlementViewSet(viewsets.ModelViewSet):
    queryset = Settlement.objects.all()

    serializer_class = SettlementSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=["post"])
    def mark_as_settled(self, request, pk=None):
        settlement = self.get_object()
        settlement.mark_as_settled()
        return Response(SettlementSerializer(settlement).data)

    def get_serializer_context(self):
        return {"request": self.request}
