#!/bin/sh

python manage.py migrate --fake-initial --no-input
python manage.py collectstatic --no-input

gunicorn django_movies:application --bind 0.0.0.0:8000