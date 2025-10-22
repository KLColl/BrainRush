import os

from flask import Flask, redirect, url_for
from flask_login import LoginManager, login_manager
from app.gamesDB import db
from app.models.user import User

login_manager = LoginManager()


def create_app():
    app = Flask(__name__)

    app.config.from_mapping(
        SECRET_KEY=os.environ.get("SECRET_KEY", "dev-secret"),
    )
    os.makedirs(app.instance_path, exist_ok=True)

    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///../instance/brainrush.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login" # redirect here if not logged in

    from app.routes.main import main_bp
    from app.routes.games import games_bp
    from app.routes.arithmetic import arithmetic_bp
    from app.routes.auth import auth_bp
    from app.routes.profile import profile_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(games_bp)
    app.register_blueprint(arithmetic_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(profile_bp)

    with app.app_context():
        db.create_all()

    return app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))