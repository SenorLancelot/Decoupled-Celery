from datetime import datetime

import pytz
from flask import send_file

from src.wsgi import service, db
from src.models import Store, BusinessHours, StoreStatus, Report
from src.celery.tasks import generate_report_task


@service.route("/trigger_report", methods=["POST"])
def trigger_report():
    rep_timestamp = datetime(2023, 1, 25, 0, 0, 0, 0, pytz.utc)
    file_name = f"report_{rep_timestamp.strftime('%Y-%m-%d')}.csv"
    report = Report(active=False, file_path=file_name)

    db.session.add(report)
    db.session.commit()

    # Enqueue the background task
    generate_report_task.delay(rep_timestamp, report.id)

    return {"status": "success", "report_id": report.id}


@service.route("/report/<int:report_id>", methods=["GET"])
def get_report(report_id):
    report = Report.query.get(report_id)

    if report:
        if report.active:
            # If the report is active, send the CSV file for download
            csv_filename = report.file_path
            return send_file(
                csv_filename,
                as_attachment=True,
                download_name=f"report_{csv_filename}",
            )
        else:
            # If the report is not active, return status:running
            return {"status": "running"}

    return {"status": "failed", "message": "Report not found"}
