from __future__ import print_function # In python 2.7
import sys
from flask import (Flask, flash, render_template, request, redirect, url_for)
from flask_sqlalchemy import SQLAlchemy
import datetime, time
from flask_login import LoginManager

import os
from config import basedir
from flask_bcrypt import Bcrypt

from flask_admin import Admin, BaseView, expose
from flask_admin.contrib.sqla import ModelView

app = Flask(__name__)
app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)
app.config.from_object('config')
lm  = LoginManager()

lm.init_app(app)
lm.login_view = 'login'
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
admin = Admin(app)
BaseView = BaseView
expose = expose
ModelView = ModelView

from app import views, models