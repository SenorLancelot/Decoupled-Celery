from src.wsgi import service, db

from datetime import datetime, timedelta
import pytz
import pandas as pd
from tqdm import tqdm
from src.models import Store, BusinessHours, StoreStatus, Report


def normalize_db():

    with service.app_context():
        business_hours_store_ids = (
            db.session.query(BusinessHours.store_id).distinct().all()
        )

        store_status_store_ids = db.session.query(StoreStatus.store_id).distinct().all()

        store_store_ids = db.session.query(Store.store_id).distinct().all()

        all_store_ids = list(
            set(business_hours_store_ids + store_status_store_ids + store_store_ids)
        )

        all_store_ids = [store_id[0] for store_id in all_store_ids]

        for store_id in all_store_ids:
            if not db.session.query(Store).filter(Store.store_id == store_id).first():
                # Create a new row with the specified logic
                new_store = Store(store_id=store_id, timezone_str="America/Chicago")
                db.session.add(new_store)

        for store_id in all_store_ids:
            for day_of_week in range(7):
                if not BusinessHours.query.filter_by(
                    store_id=store_id, day_of_week=day_of_week
                ).first():
                    # Create a new entry with the specified logic
                    new_business_hours = BusinessHours(
                        store_id=store_id,
                        day_of_week=day_of_week,
                        start_time_local="00:00:00",
                        end_time_local="23:59:59",
                    )
                    db.session.add(new_business_hours)
        db.session.commit()


def truncate_timestamp(timestamp_str):
    if timestamp_str and len(timestamp_str) >= 19:
        return timestamp_str[:19]
    return None


def generate_report(report_timestamp, report_id):

    normalize_db()
    with service.app_context():

        report_timestamp_utc = report_timestamp
        one_week_ago = report_timestamp_utc - timedelta(days=7)
        store_ids = db.session.query(Store.store_id).distinct().all()
        store_ids = [store_id[0] for store_id in store_ids]
        report_data = list()
        i = 0
        for store_id in tqdm(store_ids, desc="Processing stores", unit="store"):

            report_entry = {
                "store_id": store_id,
                "uptime_last_hour": 0,
                "uptime_last_day": 0,
                "uptime_last_week": 0,
                "downtime_last_hour": 0,
                "downtime_last_day": 0,
                "downtime_last_week": 0,
            }

            uptime_last_week = 0
            uptime_last_day = 0
            uptime_last_hour = 0
            downtime_last_week = 0
            downtime_last_day = 0
            downtime_last_hour = 0
            # Retrieve objects for Store table
            store_entry = Store.query.filter_by(store_id=store_id).first()

            # Retrieve objects for BusinessHours table
            business_hours_entries = BusinessHours.query.filter_by(
                store_id=store_id
            ).all()

            status_entries = StoreStatus.query.filter(
                StoreStatus.store_id == store_id,
            ).all()

            store_dict = {
                "store_id": store_entry.store_id,
                "timezone_str": store_entry.timezone_str,
            }
            business_hours_dicts = [
                {
                    "day_of_week": bh.day_of_week,
                    "start_time_local": bh.start_time_local,
                    "end_time_local": bh.end_time_local,
                }
                for bh in business_hours_entries
            ]
            status_dicts = [
                {"timestamp_utc": status.timestamp_utc, "status": status.status}
                for status in status_entries
            ]
            default_status_dict = {"timestamp_utc": [], "status": []}
            status_df = (
                pd.DataFrame(status_dicts)
                if status_dicts
                else pd.DataFrame(default_status_dict)
            )
            store_df = pd.DataFrame([store_dict])
            business_hours_df = pd.DataFrame(business_hours_dicts)

            if i < 2:
                print(f"Store ID: {store_id}")
                print("Store DataFrame:")
                print(store_df)
                print("\nBusiness Hours DataFrame:")
                print(business_hours_df)
                print("\nStatus DataFrame:")
                print(status_df)
                print("\n" + "=" * 30)

            timezone_str = store_df["timezone_str"][0]
            report_timestamp_utc = report_timestamp_utc.replace(tzinfo=pytz.utc)
            report_timestamp_local = report_timestamp_utc.astimezone(
                pytz.timezone(timezone_str)
            )

            status_df["timestamp_utc"] = status_df["timestamp_utc"].apply(
                truncate_timestamp
            )

            status_df["timestamp_utc"] = pd.to_datetime(
                status_df["timestamp_utc"], format="%Y-%m-%d %H:%M:%S"
            ).dt.tz_localize("UTC")

            status_df["timestamp_local"] = status_df["timestamp_utc"].dt.tz_convert(
                timezone_str
            )
            status_df_filtered = status_df[
                (status_df["timestamp_utc"] >= one_week_ago)
                & (status_df["timestamp_utc"] <= report_timestamp_utc)
            ]

            business_hours_df["start_time_obj"] = business_hours_df[
                "start_time_local"
            ].apply(lambda x: datetime.strptime(x, "%H:%M:%S").time())
            business_hours_df["end_time_obj"] = business_hours_df[
                "end_time_local"
            ].apply(lambda x: datetime.strptime(x, "%H:%M:%S").time())

            one_week_ago = report_timestamp_utc - timedelta(days=7)

            for day_of_week in range(7):
                business_hours_for_day = business_hours_df[
                    business_hours_df["day_of_week"] == day_of_week
                ]

                status_entries_for_day = status_df_filtered[
                    status_df_filtered["timestamp_local"].dt.dayofweek == day_of_week
                ]

                for _, business_hours_row in business_hours_for_day.iterrows():
                    start_time_obj = business_hours_row["start_time_obj"]
                    end_time_obj = business_hours_row["end_time_obj"]

                    business_hours_duration = (
                        datetime.combine(datetime.today(), end_time_obj)
                        - datetime.combine(datetime.today(), start_time_obj)
                    ).seconds / 3600

                    uptime_last_week += business_hours_duration

                    if (
                        day_of_week
                        == (report_timestamp_utc - timedelta(days=1)).weekday()
                    ):
                        uptime_last_day += business_hours_duration

                    if (
                        start_time_obj
                        <= (report_timestamp_utc - timedelta(hours=1)).time()
                        <= end_time_obj
                    ):
                        uptime_last_hour = 1

                for _, status_row in status_entries_for_day.iterrows():

                    if status_row["status"] == "inactive":
                        status_time_local = status_row["timestamp_local"].time()

                        if any(
                            (
                                business_hours_row["start_time_obj"]
                                <= status_time_local
                                <= business_hours_row["end_time_obj"]
                            )
                            for _, business_hours_row in business_hours_for_day.iterrows()
                        ):
                            downtime_last_week += 0.5
                            uptime_last_week -= 0.5

                            if (
                                day_of_week
                                == (report_timestamp_utc - timedelta(days=1)).weekday()
                            ):
                                downtime_last_day += 0.5
                                uptime_last_day -= 0.5

                            if status_row["timestamp_local"] >= (
                                report_timestamp_local - timedelta(hours=1)
                            ):
                                downtime_last_hour += 0.5
                                uptime_last_hour -= 0.5

            report_entry["uptime_last_week"] = uptime_last_week
            report_entry["uptime_last_day"] = uptime_last_day
            report_entry["uptime_last_hour"] = uptime_last_hour
            report_entry["downtime_last_week"] = downtime_last_week
            report_entry["downtime_last_day"] = downtime_last_day
            report_entry["downtime_last_hour"] = downtime_last_hour
            report_data.append(report_entry)

        report_data_df = pd.DataFrame(report_data)
        csv_filename = f"report_{report_timestamp_utc.strftime('%Y-%m-%d')}.csv"
        report_data_df.to_csv(csv_filename, index=False)
        report = Report.query.get(report_id)
        report.active = True
        db.session.commit()
