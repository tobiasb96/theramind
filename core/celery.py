import os

from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")


app = Celery("app")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Configure Celery to handle Heroku dyno restarts
# These settings ensure tasks are requeued when workers are terminated
app.conf.task_acks_late = True  # Only acknowledge tasks after they're completed
app.conf.task_reject_on_worker_lost = True  # Requeue tasks if worker is terminated
app.conf.task_acks_on_failure_or_timeout = False  # Don't ack tasks that fail or timeout
app.conf.broker_transport_options = {
    "visibility_timeout": 43200,  # 12 hours (in seconds)
    "max_retries": 5,  # Maximum number of retries for connection issues
}

# Load task modules from all registered Django apps.
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
