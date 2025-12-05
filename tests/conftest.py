# =============================================================================
# tests/conftest.py — Fixtures de Prueba con BD Real
# =============================================================================

import os
import pytest
from app import create_app
from app.extensions import db
from app.config import Config


class TestConfig(Config):
    TESTING = True
    # La URI viene del docker-compose.dev.yml o usa valores por defecto para local
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://gore:test_password@localhost:5432/gore_nuble_test"
    )
    WTF_CSRF_ENABLED = False


@pytest.fixture
def app():
    """Crea la aplicación conectada a la BD de pruebas."""
    app = create_app(TestConfig)

    from sqlalchemy import text

    with app.app_context():
        # Crear esquemas necesarios
        schemas = [
            "gore_financiero",
            "gore_inversion",
            "gore_actores",
            "gore_autenticacion",
            "gore_ejecucion",
            "gore_normativo",
            "gore_instancias",
            "gore_organizacion",
        ]
        for schema in schemas:
            db.session.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema}"))
        db.session.commit()

        db.create_all()  # Crear tablas reales
        yield app
        db.session.remove()
        db.drop_all()  # Limpiar BD al terminar


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def db_session(app):
    """Retorna la sesión de BD para insertar datos de prueba."""
    return db.session
