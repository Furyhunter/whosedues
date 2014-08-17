from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from whosedues.config import configure

app = Flask(__name__)
login_manager = LoginManager(app)
db = SQLAlchemy(app)
db.init_app(app)

login_manager.init_app(app)
configure(app)


import whosedues.views
import whosedues.views_admin
import whosedues.models
