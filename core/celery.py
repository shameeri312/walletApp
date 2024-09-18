import os
from celery import Celery
from celery.schedules import crontab
from datetime import timedelta

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

app = Celery("walletApp")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
