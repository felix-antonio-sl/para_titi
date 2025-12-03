# =============================================================================
# app/models/financiero.py — Modelos de gore_financiero (v4.1)
# Exactamente alineado con modelo_v4_1_estructura.sql
# =============================================================================

from datetime import date
from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Convenio(db.Model):
    """
    Convenios de transferencia/ejecución.
    Tabla: gore_financiero.convenio
    """
    __tablename__ = 'convenio'
    __table_args__ = {'schema': 'gore_financiero'}

    id = db.Column(UUID(as_uuid=True), primary_key=True)  # Sin default, viene de gore_objeto
    iniciativa_id = db.Column(UUID(as_uuid=True), db.ForeignKey('gore_inversion.iniciativa.id'), nullable=False)
    numero_resolucion = db.Column(db.String(50))
    fecha_resolucion = db.Column(db.Date)
    fecha_inicio = db.Column(db.Date, nullable=False)
    fecha_termino = db.Column(db.Date, nullable=False)
    monto_total = db.Column(db.Numeric(18, 2), nullable=False)
    entidad_ejecutora_id = db.Column(UUID(as_uuid=True), db.ForeignKey('gore_actores.entidad.id'), nullable=False)
    representante_legal_id = db.Column(UUID(as_uuid=True), db.ForeignKey('gore_actores.persona.id'))  # FK a gore_actores.persona
    documento_id = db.Column(UUID(as_uuid=True))  # FK a gore_documental.documento
    estado = db.Column(db.String(30), default='ELABORACION')  # ENUM public.estado_convenio
    observaciones = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    # Relaciones
    cuotas = db.relationship('Cuota', backref='convenio', lazy='dynamic', order_by='Cuota.numero')
    problemas = db.relationship('ProblemaIPR', backref='convenio', lazy='dynamic')
    entidad_ejecutora = db.relationship('Entidad', backref='convenios_ejecutados', foreign_keys=[entidad_ejecutora_id])
    representante_legal = db.relationship('Persona', backref='convenios_representados', foreign_keys=[representante_legal_id])

    @property
    def cuotas_pagadas_monto(self):
        """Suma de cuotas pagadas."""
        return sum(c.monto for c in self.cuotas if c.estado == 'PAGADA') or 0

    @property
    def avance_financiero(self):
        """Porcentaje de avance financiero."""
        if not self.monto_total or self.monto_total == 0:
            return 0
        return round((float(self.cuotas_pagadas_monto) / float(self.monto_total)) * 100, 1)

    def esta_vencido(self):
        """Verifica si el convenio está vencido."""
        if not self.fecha_termino:
            return False
        return date.today() > self.fecha_termino and self.estado not in ('CERRADO', 'FINIQUITADO')

    def __repr__(self):
        return f'<Convenio {self.numero_resolucion}>'


class Cuota(db.Model):
    """
    Programación de pagos por cuotas.
    Tabla: gore_financiero.cuota
    """
    __tablename__ = 'cuota'
    __table_args__ = {'schema': 'gore_financiero'}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    convenio_id = db.Column(UUID(as_uuid=True), db.ForeignKey('gore_financiero.convenio.id'), nullable=False)
    numero = db.Column(db.Integer, nullable=False)
    monto = db.Column(db.Numeric(18, 2), nullable=False)
    es_anticipo = db.Column(db.Boolean, default=False)
    fecha_programada = db.Column(db.Date)
    estado = db.Column(db.String(30), default='PENDIENTE')  # ENUM public.estado_cuota
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    def esta_vencida(self):
        """Verifica si la cuota está vencida."""
        if not self.fecha_programada:
            return False
        return date.today() > self.fecha_programada and self.estado == 'PENDIENTE'

    def __repr__(self):
        return f'<Cuota {self.numero} - {self.convenio_id}>'
