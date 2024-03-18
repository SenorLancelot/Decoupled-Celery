import time, datetime
import random

import pytz
from flask import send_file

from src.celery.start import celery_app
from src.utils import generate_report
from src.wsgi import service, db
from src.models import Store, BusinessHours, StoreStatus, Report
from src.tasks import celery_app


@service.route("/trigger_report", methods=["POST"])
def trigger_report():
    rep_timestamp = datetime(2023, 1, 25, 0, 0, 0, 0, pytz.utc)
    file_name = f"report_{rep_timestamp.strftime('%Y-%m-%d')}.csv"
    report = Report(active=False, file_path=file_name)

    db.session.add(report)
    db.session.commit()
    generate_report(rep_timestamp, report.id)

    return {"status": "success", "report_id": report.id}


@service.route("/report/<int:report_id>", methods=["GET"])
def get_report(report_id):
    report = Report.query.get(report_id)

    if report:
        if report.active:
            csv_filename = report.file_path
            return send_file(
                csv_filename,
                as_attachment=True,
                download_name=f"report_{csv_filename}",
            )
        else:
            return {"status": "running"}

    return {"status": "failed", "message": "Report not found"}


@service.route("/", methods=["GET"])
def index():
    return {"status": "healthy"}


@service.route("/add", methods=["GET"])
def add():
    num_tasks = 10
    tasks = []
    for i in range(num_tasks):
        time.sleep(2 * random.random())  # Random delay
        tasks.append(celery_app.send_task("addTask", (i, 3)))  # Send task by name
        print("Sent task:", i)

    for task in tasks:
        result = task.get()
        print("Received result:", result)

    return {"status": "success", "message": "Tasks completed"}
