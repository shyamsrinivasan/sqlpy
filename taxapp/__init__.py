from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
import os


db = SQLAlchemy()
migrate = Migrate()
csrf = CSRFProtect()
login_manager = LoginManager()
flask_bcrypt = Bcrypt()


def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # application configuration
    app.config.from_object('config.DevConfig')

    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'admin.login_home'

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    from .admin import admin_bp

    # register blueprints
    app.register_blueprint(admin_bp)

    db.init_app(app)
    migrate.init_app(app)
    with app.app_context():
        db.create_all()

    return app

