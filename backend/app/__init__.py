from flask import Flask
from flask_cors import CORS

from app.core.config import Config
from app.core.extensions import db, migrate, jwt, bcrypt
from app.core.logger import setup_structured_logging
from app.core.middleware import register_middleware
import app.models  # Register all ORM models cleanly
from app.core.exceptions import APIException

def create_app(config_class=Config, test_config=None):
    app = Flask(__name__)
    app.config.from_object(config_class)
    if test_config:
        app.config.update(test_config)

    # Initialize Logging & Correlation ID Middleware
    setup_structured_logging(app)
    register_middleware(app)

    # Initialize Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            app.logger.warning(f"Could not auto-create tables on startup: {e}")
    jwt.init_app(app)
    bcrypt.init_app(app)
    CORS(app, supports_credentials=True)

    # Global Error Handler
    @app.errorhandler(APIException)
    def handle_api_exception(error):
        return error.to_dict(), error.status_code

    # Security Headers Middleware
    @app.after_request
    def set_security_headers(response):
        response.headers['X-Frame-Options'] = 'SAMEORIGIN'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; connect-src 'self' http: https:;"
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        return response

    # Register Blueprints / Namespaces
    from app.api.v1 import blueprint as api_v1
    app.register_blueprint(api_v1, url_prefix='/api/v1')

    return app
