from flask import Flask
from flask_mongoengine import MongoEngine
from flask_login import LoginManager
import logging

# create and configure the app
app = Flask(__name__)

log = logging.getLogger('werkzeug')
log.setLevel(logging.INFO)

app.config['MONGODB_SETTINGS'] = {
    'db': 'squirrel',
    'host': 'mongodb://localhost:27017/'
}

db = MongoEngine(app)
app.config['SECRET_KEY'] = 'development'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.session_protection = "strong"

from neuralabs.views import *
