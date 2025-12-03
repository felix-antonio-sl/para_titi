# =============================================================================
# app/config.py — Configuración de la aplicación
# =============================================================================

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Configuración base."""

    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-cambiar')

    # SQLAlchemy — Conexión a v4.1
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://gore:gore_dev_2025@localhost:5432/gore_nuble'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # Paginación
    ITEMS_PER_PAGE = 20
