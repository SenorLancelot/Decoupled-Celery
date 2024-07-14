from src.wsgi import service, db
from src.views import *
from src.models import *

if __name__ == "__main__":
    with service.app_context():
        db.create_all()
        db.session.commit()
    service.run(debug=True, port=8000, host="0.0.0.0")
