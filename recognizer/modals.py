from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    uname = db.Column(db.String(50), unique=True)
    email = db.Column(db.String, unique=True)
    image = db.Column(db.LargeBinary)