import asyncio
from datetime import datetime

import pytz
from celery import Celery
from flask import Flask, Response, send_file
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from flask_migrate import Migrate

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from datetime import datetime, timedelta, timezone
import pytz
from sqlalchemy.orm import aliased
from tqdm import tqdm

service = Flask(__name__)
service.config["SQLALCHEMY_DATABASE_URI"] = (
    "postgresql://postgres:example@192.168.1.118:5432/scale"
)
db = SQLAlchemy()


migrate = Migrate(service, db)

db.init_app(service)
