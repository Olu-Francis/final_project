from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

# Initialize the Database
db = SQLAlchemy()
migrate = Migrate()
# Flask Login To do
login_manager = LoginManager()


def create_app():
    app = Flask(__name__, static_folder="static")
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = "main.login"

    from .models import Users

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.get(user_id)

    from .routes import main
    app.register_blueprint(main)

    with app.app_context():
        db.create_all()

    return app
