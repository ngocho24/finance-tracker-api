from flask import Flask, jsonify # Added jsonify
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

    # CRITICAL: Import models here so migrations and routes can see them
    from app.models import db, bcrypt, User, Transaction 

    db.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints
    from app.routes.auth import auth_bp
    from app.routes.transactions import trans_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(trans_bp, url_prefix='/api/transactions')

    # --- GLOBAL ERROR HANDLERS ---
    # These ensure the API always returns JSON, never HTML

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "error": "Bad Request",
            "message": str(error.description)
        }), 400

    @app.errorhandler(401)
    def unauthorized(error):
        return jsonify({
            "error": "Unauthorized",
            "message": "Invalid or missing authentication token"
        }), 401

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Not Found",
            "message": "The requested URL was not found on the server"
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback() # Protects DB integrity during crashes
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred on the server"
        }), 500

    return app