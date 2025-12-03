# =============================================================================
# app/models/reuniones.py — Modelos de reuniones de crisis (v4.1.2)
# Alineado con:
#   - gore_instancias.instancia_colectiva
#   - gore_instancias.reunion_crisis
#   - gore_instancias.punto_tabla
#   - gore_instancias.contexto_punto_crisis
# =============================================================================

from datetime import datetime
import uuid

from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from app.extensions import db


class TipoInstanciaColectiva(db.Model):
    """Catálogo de tipos de instancia colectiva."""

    __tablename__ = 'tipo_instancia_colectiva'
    __table_args__ = {'schema': 'gore_instancias'}

    id = db.Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    codigo = db.Column(db.String(30), unique=True, nullable=False)
    nombre = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text)
    periodicidad = db.Column(db.String(50))
    quorum_minimo = db.Column(db.Integer)
    genera_acta = db.Column(db.Boolean, default=True)
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    instancias = db.relationship('InstanciaColectiva', backref='tipo', lazy='dynamic')

    @classmethod
    def reunion_crisis(cls):
        """Obtiene el tipo REUNION_CRISIS si existe."""
        return cls.query.filter_by(codigo='REUNION_CRISIS').first()

    def __repr__(self) -> str:  # pragma: no cover
        return f'<TipoInstancia {self.codigo}>'


class InstanciaColectiva(db.Model):
    """Sesiones de comités, CDR, mesas de trabajo (dominio gore_instancias)."""

    __tablename__ = 'instancia_colectiva'
    __table_args__ = {'schema': 'gore_instancias'}

    id = db.Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tipo_id = db.Column(PG_UUID(as_uuid=True), db.ForeignKey('gore_instancias.tipo_instancia_colectiva.id'), nullable=False)
    numero = db.Column(db.Integer)
    anio = db.Column(db.Integer)
    fecha = db.Column(db.DateTime, nullable=False)
    lugar = db.Column(db.String(200))
    estado = db.Column(db.String(20), default='CONVOCADA', nullable=False)  # ENUM public.estado_instancia
    quorum_presente = db.Column(db.Integer)
    presidente_cargo_id = db.Column(PG_UUID(as_uuid=True))
    presidente_persona_id = db.Column(PG_UUID(as_uuid=True))
    secretario_id = db.Column(PG_UUID(as_uuid=True))
    acta_documento_id = db.Column(PG_UUID(as_uuid=True))
    observaciones = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    puntos = db.relationship(
        'PuntoTabla',
        backref='instancia',
        lazy='dynamic',
        order_by='PuntoTabla.numero',
        cascade='all, delete-orphan',
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f'<InstanciaColectiva {self.id} [{self.estado}]>'


class ReunionCrisis(db.Model):
    """Especialización de InstanciaColectiva para reuniones de crisis IPR.

    Morfismo monomórfico ι: ReunionCrisis ↪ InstanciaColectiva (id compartido).
    """

    __tablename__ = 'reunion_crisis'
    __table_args__ = {'schema': 'gore_instancias'}

    id = db.Column(
        PG_UUID(as_uuid=True),
        db.ForeignKey('gore_instancias.instancia_colectiva.id', ondelete='CASCADE'),
        primary_key=True,
    )
    hora_inicio = db.Column(db.Time)
    hora_fin = db.Column(db.Time)
    iniciada_en = db.Column(db.DateTime)
    finalizada_en = db.Column(db.DateTime)
    resumen = db.Column(db.Text)
    organizador_id = db.Column(PG_UUID(as_uuid=True), db.ForeignKey('gore_autenticacion.usuario.id'))
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    instancia = db.relationship('InstanciaColectiva', backref=db.backref('crisis', uselist=False))
    organizador = db.relationship('Usuario', foreign_keys=[organizador_id])

    # --- Propiedades delegadas a instancia -------------------------------------------------

    @property
    def fecha(self):
        return self.instancia.fecha if self.instancia else None

    @property
    def lugar(self):
        return self.instancia.lugar if self.instancia else None

    @property
    def estado(self):
        return self.instancia.estado if self.instancia else None

    @estado.setter
    def estado(self, value: str) -> None:
        if self.instancia:
            self.instancia.estado = value

    @property
    def temas(self):
        """Atajo para los puntos de tabla de la instancia."""
        return self.instancia.puntos if self.instancia else []

    @property
    def titulo(self) -> str:
        """Título de la reunión (almacenado en observaciones de instancia)."""
        return self.instancia.observaciones if self.instancia else ''

    @property
    def tipo(self) -> str:
        """Tipo de reunión (del tipo de instancia colectiva)."""
        if self.instancia and self.instancia.tipo:
            return self.instancia.tipo.codigo
        return 'REUNION_CRISIS'

    # --- Comportamiento de flujo -----------------------------------------------------------

    def iniciar(self) -> bool:
        """Inicia la reunión: CONVOCADA → EN_SESION."""
        if self.estado == 'CONVOCADA':
            self.estado = 'EN_SESION'
            self.iniciada_en = datetime.utcnow()
            if self.hora_inicio is None:
                self.hora_inicio = self.iniciada_en.time()
            return True
        return False

    def finalizar(self, resumen_texto: str | None = None) -> bool:
        """Finaliza la reunión: EN_SESION → CERRADA."""
        if self.estado == 'EN_SESION':
            self.estado = 'CERRADA'
            self.finalizada_en = datetime.utcnow()
            if resumen_texto:
                self.resumen = resumen_texto
            return True
        return False

    # --- Factoría --------------------------------------------------------------------------

    @classmethod
    def crear(
        cls,
        *,
        fecha: datetime,
        titulo: str | None = None,
        lugar: str | None = None,
        hora_inicio=None,
        organizador_id=None,
    ) -> 'ReunionCrisis':
        """Crea InstanciaColectiva + ReunionCrisis atómicamente.

        - tipo_instancia_colectiva.codigo = 'REUNION_CRISIS'
        - observaciones de la instancia se usan para guardar el título.
        """
        from app.extensions import db  # import local para evitar ciclos

        tipo = TipoInstanciaColectiva.reunion_crisis()
        if not tipo:
            raise RuntimeError('TipoInstanciaColectiva "REUNION_CRISIS" no existe en la BD')

        instancia = InstanciaColectiva(
            tipo_id=tipo.id,
            fecha=fecha,
            lugar=lugar,
            estado='CONVOCADA',
            observaciones=titulo,
        )
        db.session.add(instancia)
        db.session.flush()

        reunion = cls(
            id=instancia.id,
            hora_inicio=hora_inicio,
            organizador_id=organizador_id,
        )
        db.session.add(reunion)

        return reunion

    def __repr__(self) -> str:  # pragma: no cover
        return f'<ReunionCrisis {self.id} [{self.estado}]>'


class PuntoTabla(db.Model):
    """Punto de agenda de una instancia colectiva (gore_instancias.punto_tabla)."""

    __tablename__ = 'punto_tabla'
    __table_args__ = {'schema': 'gore_instancias'}

    id = db.Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instancia_id = db.Column(PG_UUID(as_uuid=True), db.ForeignKey('gore_instancias.instancia_colectiva.id'), nullable=False)
    numero = db.Column(db.Integer, nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # ENUM public.tipo_punto_tabla
    materia = db.Column(db.Text, nullable=False)
    presentador_id = db.Column(PG_UUID(as_uuid=True))
    objeto_relacionado_id = db.Column(PG_UUID(as_uuid=True))
    estado = db.Column(db.String(20), default='PENDIENTE', nullable=False)  # ENUM public.estado_punto
    resumen_discusion = db.Column(db.Text)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    contexto_crisis = db.relationship(
        'ContextoPuntoCrisis',
        backref='punto_tabla',
        uselist=False,
        cascade='all, delete-orphan',
    )

    # --- Aliases de compatibilidad ---------------------------------------------------------

    @property
    def titulo(self) -> str:
        """Alias para materia (el código de rutas usa titulo)."""
        return self.materia

    @titulo.setter
    def titulo(self, value: str) -> None:
        self.materia = value

    @property
    def orden(self) -> int:
        """Alias para numero (compatibilidad con templates)."""
        return self.numero

    @property
    def descripcion(self) -> str | None:
        """Descripción del tema (desde contexto de crisis si existe)."""
        if self.contexto_crisis:
            return self.contexto_crisis.notas
        return None

    @property
    def notas(self) -> str | None:
        """Notas/resumen de discusión."""
        return self.resumen_discusion

    @property
    def iniciativa(self):
        """Iniciativa relacionada (desde contexto de crisis si existe)."""
        if self.contexto_crisis:
            return self.contexto_crisis.iniciativa
        return None

    def __repr__(self) -> str:  # pragma: no cover
        return f'<PuntoTabla {self.numero}: {self.materia[:30]}>'


class ContextoPuntoCrisis(db.Model):
    """Contexto de crisis para un punto de tabla.

    Implementa Target = Iniciativa ⊔ ProblemaIPR ⊔ AlertaIPR ⊔ CompromisoOperativo.
    iniciativa_id se deriva siempre en BD vía trigger.
    """

    __tablename__ = 'contexto_punto_crisis'
    __table_args__ = {'schema': 'gore_instancias'}

    id = db.Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    punto_tabla_id = db.Column(
        PG_UUID(as_uuid=True),
        db.ForeignKey('gore_instancias.punto_tabla.id', ondelete='CASCADE'),
        unique=True,
        nullable=False,
    )
    target_tipo = db.Column(db.String(20), nullable=False)
    target_id = db.Column(PG_UUID(as_uuid=True), nullable=False)
    notas = db.Column(db.Text)
    iniciativa_id = db.Column(PG_UUID(as_uuid=True), db.ForeignKey('gore_inversion.iniciativa.id'), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    iniciativa = db.relationship('Iniciativa')

    def __repr__(self) -> str:  # pragma: no cover
        return f'<ContextoPuntoCrisis {self.target_tipo}:{self.target_id}>'


# =============================================================================
# ALIAS PARA COMPATIBILIDAD CON app.routes.reuniones
# =============================================================================

Reunion = ReunionCrisis
TemaReunion = PuntoTabla
