from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
import os, base64

load_dotenv()

app = Flask(__name__)
app.secret_key = base64.b64encode(str(os.getenv('APP_SEC_KEY')).encode())
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///auth.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)

manager = LoginManager(app)

from main_mod import models, routers

# from main_mod import app, db
# app.app_context().push()
# db.create_all()

