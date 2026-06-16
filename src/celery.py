import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')

app = Celery('src', broker='redis://127.0.0.1:6379/0')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()


app.conf.beat_schedule = {
    'send-reminders-every-hour': {
        'task': 'events.tasks.send_event_reminder_24h_task',
        'schedule': 3600.0,
    },
    'send-started-notifications-every-15-mins': {
        'task': 'events.tasks.send_event_started_notifications_task',
        'schedule': 900.0, 
    },
}