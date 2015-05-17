from flask import Flask
from sqlalchemy import create_engine
import config
app = Flask(__name__)
app.config.from_object('config')
db_engine = create_engine(config.SQLALCHEMY_DATABASE_URI)

from app import views
# from app import models