from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .tasks import send_mail_later


# Create your views here.
@api_view(["POST"])
def Mail_Send_View(request):
    subject = request.data["subject"]
    body = request.data["body"]
    delay_time = 1

    send_mail_later.delay(subject, body, delay_time)
    return Response(
        {
            "status": "success",
            "message": "Email will be sent in 1 minute!",
        },
        status=status.HTTP_202_ACCEPTED,
    )
