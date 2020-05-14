from flask import Blueprint
main = Blueprint('main',__name__)

from . import views
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager



app = Flask(__name__)
app.config['SECRET_KEY']= '1371ce8114eac4891b9b92bcea6ecd46'