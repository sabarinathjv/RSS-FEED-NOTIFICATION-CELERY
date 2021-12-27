import os
from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rss_feeder.settings')
app = Celery('rss_feeder')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
from datetime import timedelta



@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')


app.conf.update(timezone = 'Asia/Kolkata')
app.conf.beat_schedule = {
    
    'send-notification': {
        'task': 'api.tasks.send_notification',
        'schedule':  timedelta(minutes=1),
       
    }
    
}

