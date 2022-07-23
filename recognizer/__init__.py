from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from . import config
from os import path
from flask_login import LoginManager

DB_NAME = config.DB_NAME
SECRET_KEY = config.SECRET
DB_URI = config.URI

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=True
    db.init_app(app)

    from .auth import auth

    app.register_blueprint(auth, url_prefix='/')

    from .modals import User

    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    
    return app

def create_database(app):
    if not path.exists(DB_NAME):
        db.create_all(app=app)