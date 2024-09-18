#!/bin/sh

. /usr/src/app/venv/bin/activate

# Run database migrations
python manage.py migrate
# Start the Django application
python manage.py runserver 0.0.0.0:8000
