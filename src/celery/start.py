from celery import Celery

celery_app = Celery(
    "scale",
    broker="pyamqp://guest@localhost//",
    accept_content=["application/json"],
    result_serializer="json",
    task_serializer="json",
    result_expires=None,
)

celery_app.autodiscover_tasks()
