from celery import shared_task
from .views import *










@shared_task(bind=True)
def send_notification(a):
    bulk_notification()
    return "done"








