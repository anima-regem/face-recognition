from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    uname = db.Column(db.String(50), unique=True)
    phone = db.Column(db.String(10), unique=True)
    otp = db.Column(db.String)
    email = db.Column(db.String, unique=True)
    image = db.Column(db.LargeBinary)

    logged = False