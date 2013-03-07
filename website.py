# coding=utf-8
__author__ = 'liuwei'

import os
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from jinja2 import FileSystemLoader
from config import TEMPLATE_FOLDER, STATIC_FOLDER, SESSION_PATH
from session import SqliteSessionInterface
from flaskext.bcrypt import Bcrypt

app = Flask(__name__)
app.config.from_object('config')
app.static_folder = STATIC_FOLDER
app.jinja_loader = FileSystemLoader(TEMPLATE_FOLDER)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

if not os.path.exists(SESSION_PATH):
    os.mkdir(SESSION_PATH)
    os.chmod(SESSION_PATH, int('700', 8))
app.session_interface = SqliteSessionInterface(SESSION_PATH)

from models import User
from flask.ext.login import (LoginManager, AnonymousUser)


class Anonymous(AnonymousUser):
    name = u"Anonymous"
    id = 0

    def is_authenticated(self):
        return False

    def is_active(self):
        return False

    def is_anonymous(self):
        return True

    def get_id(self):
        return 0


login_manager = LoginManager()
login_manager.anonymous_user = Anonymous
login_manager.login_view = "user.login"
login_manager.login_message = u"亲，要先登录哦"
login_manager.refresh_view = "reauth"


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


login_manager.init_app(app)

from user import user
from api import api

app.register_blueprint(user, url_prefix='/user')
app.register_blueprint(api, url_prefix='/api')

from util import datetimeformat, friendly_datetime, weekday, format_gfm

app.jinja_env.filters['datetime'] = datetimeformat
app.jinja_env.filters['friendly_datetime'] = friendly_datetime
app.jinja_env.filters['weekday'] = weekday
app.jinja_env.filters['gfm'] = format_gfm