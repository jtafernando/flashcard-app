# This whole file is basically a constructor for a Flask app instance
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager


db = SQLAlchemy()
DB_NAME = "database.db"

# Flask App Constructor
def create_app(test_config=None):
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'arawareru'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'  # database location
    db.init_app(app)  # initialize database

    # Register blueprints
    from .views import views # these imports don't work if at top for some reason
    from .auth import auth
    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    # Register Database models
    from .deck import Deck
    from .note import Note
    from .flashcard import Flashcard
    from .user import User
    create_database(app)

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'  # where user is directed if not logged in
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    """
    Checks if database exists. If not then create it.
    """
    if not path.exists('website/' + DB_NAME):
        db.create_all(app=app)
        print('Created Database!')




    