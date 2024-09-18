from mailapp.views import Mail_Send_View
from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/send-mail/", Mail_Send_View, name="send_mails"),
    path("api/", include("wallet.urls")),
    path("api-auth/", include("rest_framework.urls")),
]
