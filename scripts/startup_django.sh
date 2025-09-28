#! /bin/sh

# Django Application startup script

python manage.py collectstatic --noinput

# Write logs to stdout/stderr
gunicorn --bind 0.0.0.0:8000 --worker-class=gthread --log-level=debug --access-logfile=- --error-logfile=- config.wsgi
