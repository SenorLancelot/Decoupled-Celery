from wsgi import service, db
from models import Store, BusinessHours, StoreStatus
import pandas as pd


def insert_timezone_data():
    # Read CSV file
    with service.app_context():
        db.create_all()
        timezone_data = pd.read_csv("static/timezone_data.csv")

        for index, row in timezone_data.iterrows():
            store = Store(
                store_id=str(row["store_id"]), timezone_str=row["timezone_str"]
            )
            db.session.add(store)

        db.session.commit()


def insert_business_hours_data():

    with service.app_context():
        db.create_all()
        business_hours_data = pd.read_csv("static/business_hours_data.csv")

        for index, row in business_hours_data.iterrows():

            business_hours = BusinessHours(
                store_id=str(row["store_id"]),
                day_of_week=int(row["day"]),
                start_time_local=row["start_time_local"],
                end_time_local=row["end_time_local"],
            )
            db.session.add(business_hours)

        db.session.commit()


def insert_store_status_data():
    # Read CSV file
    with service.app_context():
        db.create_all()
        store_status_data = pd.read_csv("static/store_status_data.csv")

        for index, row in store_status_data.iterrows():
            store_status = StoreStatus(
                store_id=str(row["store_id"]),
                timestamp_utc=row["timestamp_utc"],
                status=row["status"],
            )
            db.session.add(store_status)

        db.session.commit()


if __name__ == "__main__":
    insert_timezone_data()
    insert_business_hours_data()
    insert_store_status_data()
