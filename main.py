from app import app
from app.database import db
from app.models import Inventory, Reasons, WasteLogs

with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True)
