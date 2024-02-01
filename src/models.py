from src.wsgi import db


class Store(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.String(50), unique=True, nullable=False)
    timezone_str = db.Column(db.String(50), default="America/Chicago")


class BusinessHours(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.String(50), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False)
    start_time_local = db.Column(db.String(10))
    end_time_local = db.Column(db.String(10))


class StoreStatus(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    store_id = db.Column(db.String(50), nullable=False)
    timestamp_utc = db.Column(db.String(50))
    status = db.Column(db.String(10), nullable=False, default="active")


class Report(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=False)
