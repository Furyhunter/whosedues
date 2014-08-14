from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from whosedues.config import configure

app = Flask(__name__)
login_manager = LoginManager(app)
db = SQLAlchemy(app)
db.init_app(app)

login_manager.login_view = 'login'
login_manager.login_message = 'You are not currently logged in.'
login_manager.login_message_category = 'info'

configure(app)


import whosedues.views
import whosedues.models
