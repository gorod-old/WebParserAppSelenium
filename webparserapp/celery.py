import os

from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'webparserapp.settings')

app = Celery('webparserapp')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()

app.conf.beat_schedule = {
    'run_pars_every_10_min': {
        'task': 'main.tasks.run_pars',
        'schedule': 600,
    },

    'run_pars_every_10_min_auto': {
        'task': 'main.tasks.run_pars_on_background',
        'schedule': crontab(minute=0, hour='*/1'),
        'args': ('https://docs.google.com/spreadsheets/d/1AlWBMJHv7voJmCDBAPcuzaPj2vBbcQDffgR4e2A3wNY/edit?usp=sharing',)
    }
}
app.conf.timezone = 'UTC'


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')