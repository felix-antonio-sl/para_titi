# =============================================================================
# app/models/actores.py — Modelos de gore_actores y gore_autenticacion (v4.1)
# Exactamente alineado con modelo_v4_1_estructura.sql
# =============================================================================

from flask_login import UserMixin
from app.extensions import db, login_manager
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import text
import uuid


class Persona(db.Model):
    """
    Personas naturales que participan en el sistema.
    Tabla: gore_actores.persona
    """
    __tablename__ = 'persona'
    __table_args__ = {'schema': 'gore_actores'}

    id = db.Column(UUID(as_uuid=True), primary_key=True)  # Sin default, viene de gore_objeto
    rut = db.Column(db.String(12), unique=True, nullable=False)
    nombres = db.Column(db.String(100), nullable=False)
    apellido_paterno = db.Column(db.String(100), nullable=False)
    apellido_materno = db.Column(db.String(100))
    email = db.Column(db.String(200))
    telefono = db.Column(db.String(50))
    entidad_id = db.Column(UUID(as_uuid=True), db.ForeignKey('gore_actores.entidad.id'))  # FK a gore_actores.entidad
    cargo = db.Column(db.String(200))
    activo = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    # Relaciones
    entidad = db.relationship('Entidad', backref='personas')

    @property
    def nombre_completo(self):
        """Nombre completo de la persona."""
        partes = [self.nombres, self.apellido_paterno]
        if self.apellido_materno:
            partes.append(self.apellido_materno)
        return ' '.join(partes)

    def __repr__(self):
        return f'<Persona {self.rut}>'


class Usuario(UserMixin, db.Model):
    """
    Usuarios del sistema.
    Tabla: gore_autenticacion.usuario
    Incluye extensión v4.1: rol_crisis
    """
    __tablename__ = 'usuario'
    __table_args__ = {'schema': 'gore_autenticacion'}

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    persona_id = db.Column(UUID(as_uuid=True), db.ForeignKey('gore_actores.persona.id'), nullable=False)
    username = db.Column(db.String(100), unique=True)
    rut_verificado = db.Column(db.Boolean, default=False)
    email_verificado = db.Column(db.Boolean, default=False)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    ultimo_acceso = db.Column(db.DateTime)
    intentos_fallidos = db.Column(db.Integer, default=0)
    bloqueado_hasta = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    
    # Extensión v4.1 para gestión de crisis
    rol_crisis = db.Column(db.String(30))  # ENUM gore_ejecucion.rol_crisis

    # Relaciones
    persona = db.relationship('Persona', backref=db.backref('usuario', uselist=False))

    # --- Métodos de autenticación ---
    # Nota: v4.1 no tiene password_hash en usuario
    # Para desarrollo, usamos password fijo

    def check_password(self, password):
        """Verifica la contraseña (simplificado para desarrollo)."""
        # En producción, integrar con sistema de autenticación real (LDAP, OAuth, etc.)
        return password == 'admin123'

    def get_id(self):
        """Requerido por Flask-Login."""
        return str(self.id)

    # --- Métodos de rol ---

    def es_admin_sistema(self):
        return self.rol_crisis == 'ADMIN_SISTEMA'

    def es_admin_regional(self):
        return self.rol_crisis == 'ADMIN_REGIONAL'

    def es_jefe(self):
        return self.rol_crisis == 'JEFE_DIVISION'

    def es_encargado(self):
        return self.rol_crisis == 'ENCARGADO_OPERATIVO'

    def puede_ver_todas_ipr(self):
        """Admin Sistema y Admin Regional ven todas las IPR."""
        return self.rol_crisis in ('ADMIN_SISTEMA', 'ADMIN_REGIONAL')

    def puede_verificar_compromisos(self):
        """Admin, Jefe y Admin Regional pueden verificar."""
        return self.rol_crisis in ('ADMIN_SISTEMA', 'ADMIN_REGIONAL', 'JEFE_DIVISION')

    def puede_crear_compromisos(self):
        """Todos menos encargado operativo."""
        return self.rol_crisis in ('ADMIN_SISTEMA', 'ADMIN_REGIONAL', 'JEFE_DIVISION')

    def puede_gestionar_usuarios(self):
        """Solo Admin Sistema puede gestionar usuarios."""
        return self.rol_crisis == 'ADMIN_SISTEMA'

    def puede_gestionar_divisiones(self):
        """Solo Admin Sistema puede gestionar divisiones."""
        return self.rol_crisis == 'ADMIN_SISTEMA'

    def puede_ver_division(self, division_id):
        """Verifica si puede ver una división específica."""
        if self.puede_ver_todas_ipr():
            return True
        mi_division = self.get_division_id()
        return mi_division and str(mi_division) == str(division_id)

    def get_division_id(self):
        """
        Obtiene el ID de la división del usuario usando la función de BD.
        Usa la cadena composicional: usuario → persona → dotacion → cargo → division.
        """
        try:
            result = db.session.execute(
                text("SELECT gore_ejecucion.fn_division_de_usuario(:user_id)"),
                {'user_id': self.id}
            ).scalar()
            return result
        except Exception:
            # Si la función no existe o hay error, retornar None
            return None

    def get_division(self):
        """Obtiene el objeto División del usuario."""
        from app.models.organizacion import Division
        division_id = self.get_division_id()
        if division_id:
            return Division.query.get(division_id)
        return None

    @property
    def nombre_completo(self):
        """Nombre completo desde persona asociada."""
        if self.persona:
            return self.persona.nombre_completo
        return self.username or 'Sin nombre'

    def __repr__(self):
        return f'<Usuario {self.username}>'


@login_manager.user_loader
def load_user(user_id):
    """Callback para Flask-Login."""
    try:
        return Usuario.query.get(uuid.UUID(user_id))
    except (ValueError, TypeError):
        return None
