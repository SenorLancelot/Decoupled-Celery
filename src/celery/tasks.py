import time
import random

from celery import shared_task

from src.celery.start import celery_app


@shared_task(name="addTask")  # Named task
def add(x, y):
    print("Task Add started")
    time.sleep(10 * random.random())  # Simulate a long task
    print("Task Add done")
    return x + y
