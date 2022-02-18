from flask import Flask
from app.db import DB
from app.config import Config
from app.models.base import login, babel


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    app.db = DB(app)

    login.init_app(app)
    babel.init_app(app)

    from .index import bp as index_bp
    app.register_blueprint(index_bp)

    from .users import bp as user_bp
    app.register_blueprint(user_bp)

    return app