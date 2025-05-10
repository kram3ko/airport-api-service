#!/bin/sh
set -e

# apply migrations
python manage.py migrate

# collecting static
python manage.py collectstatic --noinput

# running server
gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --threads 2

exec "$@"
