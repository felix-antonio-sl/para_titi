# =============================================================================
# app/models/catalogos.py — Modelos de catálogos y entidades auxiliares (v4.1)
# Entidades de soporte para casos de uso completos
# =============================================================================

from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Entidad(db.Model):
    """
    Personas jurídicas: GORE, municipios, servicios, organizaciones.
    Tabla: gore_actores.entidad
    Uso: Ejecutores de convenios, entidades beneficiarias.
    """
    __tablename__ = 'entidad'
    __table_args__ = {'schema': 'gore_actores'}

    id = db.Column(UUID(as_uuid=True), primary_key=True)  # Viene de gore_objeto
    rut = db.Column(db.String(12), unique=True, nullable=False)
    nombre = db.Column(db.String(300), nullable=False)
    nombre_corto = db.Column(db.String(100))
    tipo = db.Column(db.String(30), nullable=False)  # ENUM public.tipo_entidad
    comuna_id = db.Column(UUID(as_uuid=True))  # FK a gore_territorial.comuna
    direccion = db.Column(db.String(500))
    telefono = db.Column(db.String(50))
    email = db.Column(db.String(200))
    sitio_web = db.Column(db.String(300))
    fecha_constitucion = db.Column(db.Date)
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    @property
    def nombre_display(self):
        """Nombre corto si existe, sino nombre completo truncado."""
        return self.nombre_corto or (self.nombre[:50] + '...' if len(self.nombre) > 50 else self.nombre)

    def __repr__(self):
        return f'<Entidad {self.rut}>'


class Instrumento(db.Model):
    """
    Instrumentos de inversión: FNDR, PMU, etc.
    Tabla: gore_normativo.instrumento
    Uso: Clasificar IPR por tipo de financiamiento.
    """
    __tablename__ = 'instrumento'
    __table_args__ = {'schema': 'gore_normativo'}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = db.Column(db.String(20), unique=True, nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    subtitulo_presupuestario = db.Column(db.Integer)
    tipo_subtitulo = db.Column(db.String(30))  # ENUM public.tipo_subtitulo
    requiere_rs_mdsf = db.Column(db.Boolean, default=False)
    requiere_rf_dipres = db.Column(db.Boolean, default=False)
    permite_privados = db.Column(db.Boolean, default=False)
    permite_municipios = db.Column(db.Boolean, default=True)
    tope_monto_utm = db.Column(db.Numeric(12, 2))
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    # Relación con iniciativas
    iniciativas = db.relationship('Iniciativa', backref='instrumento', lazy='dynamic')

    def __repr__(self):
        return f'<Instrumento {self.codigo}>'


class InformeAvance(db.Model):
    """
    Informes de avance físico/financiero.
    Tabla: gore_ejecucion.informe_avance
    Uso: Registrar avances periódicos de convenios.
    """
    __tablename__ = 'informe_avance'
    __table_args__ = {'schema': 'gore_ejecucion'}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    convenio_id = db.Column(UUID(as_uuid=True), db.ForeignKey('gore_financiero.convenio.id'), nullable=False)
    numero = db.Column(db.Integer, nullable=False)
    tipo = db.Column(db.String(30), nullable=False)  # ENUM public.tipo_informe_avance
    periodo_desde = db.Column(db.Date, nullable=False)
    periodo_hasta = db.Column(db.Date, nullable=False)
    fecha_emision = db.Column(db.Date, server_default=db.func.current_date())
    elaborador_id = db.Column(UUID(as_uuid=True), db.ForeignKey('gore_actores.persona.id'))
    documento_id = db.Column(UUID(as_uuid=True))  # FK a gore_documental.documento
    resumen = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    # Relaciones
    convenio = db.relationship('Convenio', backref=db.backref('informes_avance', lazy='dynamic', order_by='InformeAvance.numero.desc()'))
    elaborador = db.relationship('Persona', backref='informes_elaborados')

    def __repr__(self):
        return f'<InformeAvance {self.numero} - {self.convenio_id}>'


class AvanceFisico(db.Model):
    """
    Detalle de avance físico por componente.
    Tabla: gore_ejecucion.avance_fisico
    Uso: Desglose del avance por componente de la IPR.
    """
    __tablename__ = 'avance_fisico'
    __table_args__ = {'schema': 'gore_ejecucion'}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    informe_id = db.Column(UUID(as_uuid=True), db.ForeignKey('gore_ejecucion.informe_avance.id'), nullable=False)
    componente_id = db.Column(UUID(as_uuid=True))  # FK a gore_inversion.componente
    indicador_id = db.Column(UUID(as_uuid=True))  # FK a gore_indicadores.indicador
    valor_periodo = db.Column(db.Numeric(12, 2))
    valor_acumulado = db.Column(db.Numeric(12, 2))
    porcentaje_avance = db.Column(db.Numeric(5, 2))
    observaciones = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    # Relaciones
    informe = db.relationship('InformeAvance', backref='avances_fisicos')

    def __repr__(self):
        return f'<AvanceFisico {self.porcentaje_avance}%>'
