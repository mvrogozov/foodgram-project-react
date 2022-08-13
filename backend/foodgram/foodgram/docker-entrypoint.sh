#!/bin/bash

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

echo "Start gunicorn"
gunicorn --bind 0.0.0.0:8000 foodgram.wsgi