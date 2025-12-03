# =============================================================================
# app/models/inversion.py — Modelos de gore_inversion (v4.1)
# Exactamente alineado con modelo_v4_1_estructura.sql
# =============================================================================

from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Iniciativa(db.Model):
    """
    Intervenciones Públicas Regionales (IPR).
    Tabla: gore_inversion.iniciativa
    Incluye extensiones v4.1: responsable_id, division_responsable_id, nivel_alerta, tiene_problemas_abiertos
    """
    __tablename__ = 'iniciativa'
    __table_args__ = {'schema': 'gore_inversion'}

    # Columnas base
    id = db.Column(UUID(as_uuid=True), primary_key=True)  # Sin default, viene de gore_objeto
    codigo_interno = db.Column(db.String(30), nullable=False, unique=True)
    nombre = db.Column(db.String(500), nullable=False)
    descripcion = db.Column(db.Text)
    instrumento_id = db.Column(UUID(as_uuid=True), db.ForeignKey('gore_normativo.instrumento.id'), nullable=False)
    anio_presupuestario = db.Column(db.Integer, nullable=False)
    monto_solicitado = db.Column(db.Numeric(18, 2))
    monto_aprobado = db.Column(db.Numeric(18, 2))
    estado_fsm_id = db.Column(UUID(as_uuid=True), nullable=False)
    fecha_creacion = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    fecha_cierre = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    # Extensión v4.1 para gestión de crisis
    responsable_id = db.Column(UUID(as_uuid=True), db.ForeignKey('gore_autenticacion.usuario.id'))
    division_responsable_id = db.Column(UUID(as_uuid=True), db.ForeignKey('gore_organizacion.division.id'))
    nivel_alerta = db.Column(db.String(20), default='NORMAL')  # ENUM gore_ejecucion.nivel_alerta_ipr
    tiene_problemas_abiertos = db.Column(db.Boolean, default=False)

    # Relaciones
    responsable = db.relationship('Usuario', foreign_keys=[responsable_id], backref='iniciativas_asignadas')
    division_responsable = db.relationship('Division', backref='iniciativas')
    # instrumento se define en catalogos.py via backref
    convenios = db.relationship('Convenio', backref='iniciativa', lazy='dynamic')
    problemas = db.relationship('ProblemaIPR', backref='iniciativa', lazy='dynamic')
    compromisos = db.relationship('CompromisoOperativo', 
                                   primaryjoin="Iniciativa.id==CompromisoOperativo.iniciativa_id",
                                   back_populates='iniciativa_rel', lazy='dynamic')
    alertas = db.relationship('AlertaIPR', backref='iniciativa', lazy='dynamic')

    @property
    def problemas_abiertos_count(self):
        """Cuenta problemas abiertos."""
        from app.models.crisis import ProblemaIPR
        return self.problemas.filter(
            ProblemaIPR.estado.in_(['ABIERTO', 'EN_GESTION'])
        ).count()

    @property
    def compromisos_pendientes_count(self):
        """Cuenta compromisos pendientes."""
        from app.models.crisis import CompromisoOperativo
        return self.compromisos.filter(
            CompromisoOperativo.estado.in_(['PENDIENTE', 'EN_PROGRESO'])
        ).count()

    @property
    def alertas_activas_count(self):
        """Conteo de alertas activas."""
        from app.models.crisis import AlertaIPR
        return self.alertas.filter(AlertaIPR.activa == True).count()

    def __repr__(self):
        return f'<Iniciativa {self.codigo_interno}>'


# Import para evitar circular
from app.models.crisis import ProblemaIPR, CompromisoOperativo, AlertaIPR
