import time
import random

from celery import Celery, shared_task

celery_app = Celery(
    "scale",
    broker="redis://192.168.1.118:6379/0",
    result_backend="redis://192.168.1.118:6379/0",
    accept_content=["application/json"],
    result_serializer="json",
    task_serializer="json",
    result_expires=None,
)

celery_app.autodiscover_tasks("src.celery.tasks")


@shared_task(name="addTask")  # Named task
def add(x, y):
    print("Task Add started")
    time.sleep(10 * random.random())  # Simulate a long task
    print("Task Add done")
    return x + y


#
# @celery_app.task(name="addTask")  # Named task
# def add(x, y):
#     print("Task Add started")
#     time.sleep(10 * random.random())  # Simulate a long task
#     print("Task Add done")
#     return x + y
