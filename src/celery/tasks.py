from src.celery import celery
from src.utils import generate_report


@celery.task
def generate_report_task(report_timestamp, report_id):
    generate_report(report_timestamp, report_id)
