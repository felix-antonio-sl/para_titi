# =============================================================================
# app/models/crisis.py — Modelos de gore_ejecucion para gestión de crisis (v4.1)
# Exactamente alineado con modelo_v4_1_estructura.sql
# =============================================================================

from datetime import date, datetime
from app.extensions import db
from sqlalchemy.dialects.postgresql import UUID
import uuid


class TipoCompromisoOperativo(db.Model):
    """Catálogo de tipos de compromiso operativo."""
    __tablename__ = 'tipo_compromiso_operativo'
    __table_args__ = {'schema': 'gore_ejecucion'}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = db.Column(db.String(30), unique=True, nullable=False)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)
    requiere_vinculo_ipr = db.Column(db.Boolean, default=True)
    dias_default = db.Column(db.Integer, default=7)
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    def __repr__(self):
        return f'<TipoCompromiso {self.codigo}>'


class ProblemaIPR(db.Model):
    """
    Problemas/nudos detectados en IPR.
    Tabla: gore_ejecucion.problema_ipr
    Morfismo principal: problema → iniciativa.
    """
    __tablename__ = 'problema_ipr'
    __table_args__ = {'schema': 'gore_ejecucion'}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    iniciativa_id = db.Column(UUID(as_uuid=True), db.ForeignKey('gore_inversion.iniciativa.id'), nullable=False)
    convenio_id = db.Column(UUID(as_uuid=True), db.ForeignKey('gore_financiero.convenio.id'))
    tipo = db.Column(db.String(30), nullable=False)  # ENUM gore_ejecucion.tipo_problema_ipr
    impacto = db.Column(db.String(30), nullable=False)  # ENUM gore_ejecucion.impacto_problema_ipr
    descripcion = db.Column(db.Text, nullable=False)
    impacto_descripcion = db.Column(db.Text)
    detectado_por_id = db.Column(UUID(as_uuid=True), db.ForeignKey('gore_autenticacion.usuario.id'), nullable=False)
    detectado_en = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    estado = db.Column(db.String(30), default='ABIERTO')  # ENUM gore_ejecucion.estado_problema_ipr
    solucion_propuesta = db.Column(db.Text)
    solucion_aplicada = db.Column(db.Text)
    resuelto_por_id = db.Column(UUID(as_uuid=True), db.ForeignKey('gore_autenticacion.usuario.id'))
    resuelto_en = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    # Relaciones
    detectado_por = db.relationship('Usuario', foreign_keys=[detectado_por_id], backref='problemas_detectados')
    resuelto_por = db.relationship('Usuario', foreign_keys=[resuelto_por_id], backref='problemas_resueltos')
    compromisos = db.relationship('CompromisoOperativo', backref='problema', lazy='dynamic')

    # --- Métodos ---

    def esta_abierto(self):
        """Verifica si el problema está abierto o en gestión."""
        return self.estado in ('ABIERTO', 'EN_GESTION')

    def dias_abierto(self):
        """Días desde que se detectó el problema."""
        if not self.esta_abierto():
            return 0
        return (datetime.utcnow() - self.detectado_en).days

    def __repr__(self):
        return f'<ProblemaIPR {self.id} [{self.tipo}]>'


class CompromisoOperativo(db.Model):
    """
    Compromisos operativos.
    Tabla: gore_ejecucion.compromiso_operativo
    IMPORTANTE: iniciativa_id es derivado por trigger, no insertar directamente.
    """
    __tablename__ = 'compromiso_operativo'
    __table_args__ = {'schema': 'gore_ejecucion'}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    
    # Vínculos origen (de dónde viene el compromiso)
    instancia_id = db.Column(UUID(as_uuid=True))  # FK a gore_instancias.instancia_colectiva (sin mapear)
    problema_id = db.Column(UUID(as_uuid=True), db.ForeignKey('gore_ejecucion.problema_ipr.id'))
    
    # Vínculos IPR (qué afecta) - FKs reales en v4.1
    cuota_id = db.Column(UUID(as_uuid=True), db.ForeignKey('gore_financiero.cuota.id'))
    convenio_id = db.Column(UUID(as_uuid=True), db.ForeignKey('gore_financiero.convenio.id'))
    iniciativa_id = db.Column(UUID(as_uuid=True), db.ForeignKey('gore_inversion.iniciativa.id'))
    
    # Tipo y descripción
    tipo_id = db.Column(UUID(as_uuid=True), db.ForeignKey('gore_ejecucion.tipo_compromiso_operativo.id'), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    
    # Asignación
    responsable_id = db.Column(UUID(as_uuid=True), db.ForeignKey('gore_autenticacion.usuario.id'), nullable=False)
    division_id = db.Column(UUID(as_uuid=True), db.ForeignKey('gore_organizacion.division.id'))
    
    # Plazos y estado
    fecha_limite = db.Column(db.Date, nullable=False)
    prioridad = db.Column(db.String(20), default='MEDIA')  # ENUM gore_ejecucion.prioridad_compromiso
    estado = db.Column(db.String(20), default='PENDIENTE')  # ENUM gore_ejecucion.estado_compromiso
    observaciones = db.Column(db.Text)
    completado_en = db.Column(db.DateTime)
    
    # Verificación
    verificado_por_id = db.Column(UUID(as_uuid=True), db.ForeignKey('gore_autenticacion.usuario.id'))
    verificado_en = db.Column(db.DateTime)
    
    # Auditoría
    creado_por_id = db.Column(UUID(as_uuid=True), db.ForeignKey('gore_autenticacion.usuario.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    # ==========================================================================
    # RELACIONES - Todas las FKs de v4.1 mapeadas
    # ==========================================================================
    
    # Tipo de compromiso
    tipo = db.relationship('TipoCompromisoOperativo', backref='compromisos')
    
    # Usuarios involucrados
    responsable = db.relationship('Usuario', foreign_keys=[responsable_id], backref='compromisos_asignados')
    verificado_por = db.relationship('Usuario', foreign_keys=[verificado_por_id], backref='compromisos_verificados')
    creado_por = db.relationship('Usuario', foreign_keys=[creado_por_id], backref='compromisos_creados')
    
    # Organización
    division = db.relationship('Division', backref='compromisos')
    
    # Vínculos IPR (relaciones navegables)
    iniciativa_rel = db.relationship('Iniciativa', back_populates='compromisos', foreign_keys=[iniciativa_id])
    convenio = db.relationship('Convenio', backref='compromisos', foreign_keys=[convenio_id])
    cuota = db.relationship('Cuota', backref='compromisos', foreign_keys=[cuota_id])
    
    # Historial de cambios
    historial = db.relationship('HistorialCompromiso', backref='compromiso', lazy='dynamic',
                                 order_by='HistorialCompromiso.created_at.desc()')

    # --- Métodos ---

    def esta_vencido(self):
        """Verifica si el compromiso está vencido."""
        if self.estado in ('COMPLETADO', 'VERIFICADO', 'CANCELADO'):
            return False
        return self.fecha_limite < date.today()

    def dias_restantes(self):
        """Días hasta la fecha límite (negativo si vencido)."""
        if self.estado in ('COMPLETADO', 'VERIFICADO', 'CANCELADO'):
            return None
        return (self.fecha_limite - date.today()).days

    def puede_completar(self, usuario):
        """Verifica si el usuario puede completar este compromiso."""
        return self.responsable_id == usuario.id or usuario.es_admin_sistema()

    def puede_verificar(self, usuario):
        """Verifica si el usuario puede verificar este compromiso."""
        return usuario.puede_verificar_compromisos()

    @property
    def clase_prioridad(self):
        """Clase CSS según prioridad."""
        clases = {
            'BAJA': 'text-gray-500',
            'MEDIA': 'text-blue-500',
            'ALTA': 'text-orange-500',
            'URGENTE': 'text-red-600 font-bold',
        }
        return clases.get(self.prioridad, 'text-gray-500')

    @property
    def clase_estado(self):
        """Clase CSS según estado."""
        clases = {
            'PENDIENTE': 'bg-yellow-100 text-yellow-800',
            'EN_PROGRESO': 'bg-blue-100 text-blue-800',
            'COMPLETADO': 'bg-green-100 text-green-800',
            'VERIFICADO': 'bg-emerald-100 text-emerald-800',
            'CANCELADO': 'bg-gray-100 text-gray-800',
        }
        return clases.get(self.estado, 'bg-gray-100 text-gray-800')

    def __repr__(self):
        return f'<CompromisoOperativo {self.id} [{self.estado}]>'


class HistorialCompromiso(db.Model):
    """Historial de cambios de estado de compromisos (event sourcing)."""
    __tablename__ = 'historial_compromiso'
    __table_args__ = {'schema': 'gore_ejecucion'}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    compromiso_id = db.Column(UUID(as_uuid=True),
                               db.ForeignKey('gore_ejecucion.compromiso_operativo.id', ondelete='CASCADE'),
                               nullable=False)
    estado_anterior = db.Column(db.String(20))
    estado_nuevo = db.Column(db.String(20), nullable=False)
    usuario_id = db.Column(UUID(as_uuid=True), db.ForeignKey('gore_autenticacion.usuario.id'), nullable=False)
    comentario = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    # Relaciones
    usuario = db.relationship('Usuario', backref='acciones_historial')

    def __repr__(self):
        return f'<HistorialCompromiso {self.estado_anterior} → {self.estado_nuevo}>'


class AlertaIPR(db.Model):
    """
    Alertas automáticas.
    Tabla: gore_ejecucion.alerta_ipr
    Target discriminado (tipo+id) evita span ambiguo.
    """
    __tablename__ = 'alerta_ipr'
    __table_args__ = {'schema': 'gore_ejecucion'}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    target_tipo = db.Column(db.String(30), nullable=False)  # CHECK: INICIATIVA, CONVENIO, CUOTA, COMPROMISO, PROBLEMA
    target_id = db.Column(UUID(as_uuid=True), nullable=False)
    iniciativa_id = db.Column(UUID(as_uuid=True), db.ForeignKey('gore_inversion.iniciativa.id'), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)  # ENUM gore_ejecucion.tipo_alerta_ipr
    nivel = db.Column(db.String(20), nullable=False)  # ENUM gore_ejecucion.nivel_alerta_ipr
    mensaje = db.Column(db.Text, nullable=False)
    datos_contexto = db.Column(db.JSON)  # jsonb
    activa = db.Column(db.Boolean, default=True)
    atendida_por_id = db.Column(UUID(as_uuid=True), db.ForeignKey('gore_autenticacion.usuario.id'))
    atendida_en = db.Column(db.DateTime)
    accion_tomada = db.Column(db.Text)
    generada_en = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    # Relaciones
    atendida_por = db.relationship('Usuario', backref='alertas_atendidas')

    @property
    def clase_nivel(self):
        """Clase CSS según nivel de alerta."""
        clases = {
            'INFO': 'bg-blue-100 text-blue-800 border-blue-300',
            'ATENCION': 'bg-yellow-100 text-yellow-800 border-yellow-300',
            'ALTO': 'bg-orange-100 text-orange-800 border-orange-300',
            'CRITICO': 'bg-red-100 text-red-800 border-red-300',
        }
        return clases.get(self.nivel, 'bg-gray-100 text-gray-800')

    def __repr__(self):
        return f'<AlertaIPR {self.tipo} [{self.nivel}]>'
