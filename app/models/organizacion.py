# =============================================================================
# app/models/organizacion.py — Modelos de gore_organizacion (v4.1)
# Exactamente alineado con modelo_v4_1_estructura.sql
# =============================================================================

from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Division(db.Model):
    """
    Divisiones del GORE: DIPIR, DAF, DIDESOH, etc.
    Tabla: gore_organizacion.division
    """
    __tablename__ = 'division'
    __table_args__ = {'schema': 'gore_organizacion'}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = db.Column(db.String(20), nullable=False, unique=True)
    nombre = db.Column(db.String(200), nullable=False)
    sigla = db.Column(db.String(20))
    orden_jerarquico = db.Column(db.Integer)
    jefe_cargo_id = db.Column(UUID(as_uuid=True))  # FK a gore_organizacion.cargo
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    def __repr__(self):
        return f'<Division {self.codigo}>'
