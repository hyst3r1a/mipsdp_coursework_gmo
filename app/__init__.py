from flask import Flask
from app.database import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

from app import api, dash_app

app.register_blueprint(api.api, url_prefix='/')

from app.dash_app import app as dash_app

# Mount Dash app on Flask server
dash_app.init_app(app)