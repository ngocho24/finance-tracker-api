from flask import Flask
from config import Config
from app.models import db, bcrypt
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate

migrate = Migrate()
jwt = JWTManager()

# This MUST be named exactly 'create_app'
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    from app.routes.auth import auth_bp
    from app.routes.transactions import trans_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(trans_bp, url_prefix='/api/transactions')

    return app