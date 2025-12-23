# =============================================================================
# app/__init__.py — Application Factory
# =============================================================================

from flask import Flask
from app.config import Config
from app.extensions import db, login_manager, csrf


def create_app(config_class=Config):
    """Application factory pattern."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar extensiones
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)

    # Registrar comandos CLI
    from app import cli

    cli.init_app(app)

    # Registrar blueprints
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.ipr import ipr_bp
    from app.routes.compromisos import compromisos_bp
    from app.routes.problemas import problemas_bp
    from app.routes.alertas import alertas_bp
    from app.routes.ejecutivo import ejecutivo_bp
    from app.routes.admin import admin_bp
    from app.routes.division import division_bp
    from app.routes.reuniones import reuniones_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(ipr_bp, url_prefix="/ipr")
    app.register_blueprint(compromisos_bp, url_prefix="/compromisos")
    app.register_blueprint(problemas_bp, url_prefix="/problemas")
    app.register_blueprint(alertas_bp, url_prefix="/alertas")
    app.register_blueprint(ejecutivo_bp, url_prefix="/ejecutivo")
    app.register_blueprint(admin_bp, url_prefix="/admin")
    app.register_blueprint(division_bp)
    app.register_blueprint(reuniones_bp, url_prefix="/reuniones")

    # Health check endpoint
    @app.route("/health")
    def health():
        return {"status": "ok"}, 200

    return app
