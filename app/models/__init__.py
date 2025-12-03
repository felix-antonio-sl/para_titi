# =============================================================================
# app/models/__init__.py — Exportación de modelos (v4.1 completo)
# Incluye todas las entidades necesarias para casos_uso.md
# =============================================================================

# Organización
from app.models.organizacion import Division

# Actores
from app.models.actores import Persona, Usuario

# Catálogos y auxiliares
from app.models.catalogos import Entidad, Instrumento, InformeAvance, AvanceFisico

# Inversión
from app.models.inversion import Iniciativa

# Financiero
from app.models.financiero import Convenio, Cuota

# Gestión de crisis
from app.models.crisis import (
    TipoCompromisoOperativo,
    ProblemaIPR,
    CompromisoOperativo,
    HistorialCompromiso,
    AlertaIPR
)

# Reuniones
from app.models.reuniones import Reunion, TemaReunion

__all__ = [
    # Organización
    'Division',
    # Actores
    'Persona',
    'Usuario',
    # Catálogos
    'Entidad',
    'Instrumento',
    'InformeAvance',
    'AvanceFisico',
    # Inversión
    'Iniciativa',
    # Financiero
    'Convenio',
    'Cuota',
    # Crisis
    'TipoCompromisoOperativo',
    'ProblemaIPR',
    'CompromisoOperativo',
    'HistorialCompromiso',
    'AlertaIPR',
    # Reuniones
    'Reunion',
    'TemaReunion',
]
