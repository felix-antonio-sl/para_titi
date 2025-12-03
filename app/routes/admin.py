# =============================================================================
# app/routes/admin.py — Módulo de Administración del Sistema
# Casos de uso: AS-01 a AS-12
# =============================================================================

from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from functools import wraps
from app.extensions import db
from app.models import Usuario, Persona, Division

admin_bp = Blueprint('admin', __name__)


def admin_required(f):
    """Decorador: Solo Admin Sistema puede acceder."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.puede_gestionar_usuarios():
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


# =============================================================================
# Panel Principal de Administración
# =============================================================================

@admin_bp.route('/')
@login_required
@admin_required
def index():
    """Panel principal de administración."""
    stats = {
        'total_usuarios': Usuario.query.filter_by(activo=True).count(),
        'total_divisiones': Division.query.filter_by(activo=True).count(),
        'usuarios_recientes': Usuario.query.order_by(
            Usuario.fecha_creacion.desc()
        ).limit(5).all()
    }
    return render_template('admin/index.html', stats=stats)


# =============================================================================
# Gestión de Usuarios (AS-03 a AS-06)
# =============================================================================

@admin_bp.route('/usuarios')
@login_required
@admin_required
def usuarios_lista():
    """Lista de usuarios del sistema."""
    page = request.args.get('page', 1, type=int)
    buscar = request.args.get('buscar', '')
    rol = request.args.get('rol', '')
    activo = request.args.get('activo', '')

    query = Usuario.query.join(Persona)

    if buscar:
        query = query.filter(
            db.or_(
                Persona.nombres.ilike(f'%{buscar}%'),
                Persona.apellido_paterno.ilike(f'%{buscar}%'),
                Usuario.username.ilike(f'%{buscar}%'),
                Persona.rut.ilike(f'%{buscar}%')
            )
        )

    if rol:
        query = query.filter(Usuario.rol_crisis == rol)

    if activo == '1':
        query = query.filter(Usuario.activo == True)
    elif activo == '0':
        query = query.filter(Usuario.activo == False)

    query = query.order_by(Persona.apellido_paterno, Persona.nombres)
    paginacion = query.paginate(page=page, per_page=20, error_out=False)

    roles_disponibles = [
        ('ADMIN_SISTEMA', 'Administrador del Sistema'),
        ('ADMIN_REGIONAL', 'Administrador Regional'),
        ('JEFE_DIVISION', 'Jefe de División'),
        ('ENCARGADO_OPERATIVO', 'Encargado Operativo'),
    ]

    return render_template('admin/usuarios/lista.html',
                           usuarios=paginacion.items,
                           paginacion=paginacion,
                           roles=roles_disponibles,
                           filtros={'buscar': buscar, 'rol': rol, 'activo': activo})


@admin_bp.route('/usuarios/nuevo', methods=['GET', 'POST'])
@login_required
@admin_required
def usuarios_nuevo():
    """Crear nuevo usuario (AS-03)."""
    if request.method == 'POST':
        # Datos de persona
        rut = request.form.get('rut', '').strip()
        nombres = request.form.get('nombres', '').strip()
        apellido_paterno = request.form.get('apellido_paterno', '').strip()
        apellido_materno = request.form.get('apellido_materno', '').strip()
        email = request.form.get('email', '').strip()
        telefono = request.form.get('telefono', '').strip()
        cargo = request.form.get('cargo', '').strip()

        # Datos de usuario
        username = request.form.get('username', '').strip()
        rol_crisis = request.form.get('rol_crisis')

        # Validaciones básicas
        if not all([rut, nombres, apellido_paterno, username, rol_crisis]):
            flash('Todos los campos obligatorios deben completarse.', 'error')
        elif Persona.query.filter_by(rut=rut).first():
            flash(f'Ya existe una persona con RUT {rut}.', 'error')
        elif Usuario.query.filter_by(username=username).first():
            flash(f'Ya existe un usuario con username {username}.', 'error')
        else:
            import uuid
            # Crear persona
            persona = Persona(
                id=uuid.uuid4(),
                rut=rut,
                nombres=nombres,
                apellido_paterno=apellido_paterno,
                apellido_materno=apellido_materno or None,
                email=email or None,
                telefono=telefono or None,
                cargo=cargo or None,
                activo=True
            )
            db.session.add(persona)

            # Crear usuario
            usuario = Usuario(
                persona_id=persona.id,
                username=username,
                rol_crisis=rol_crisis,
                activo=True
            )
            db.session.add(usuario)
            db.session.commit()

            flash(f'Usuario {username} creado correctamente.', 'success')
            return redirect(url_for('admin.usuarios_lista'))

    roles_disponibles = [
        ('ADMIN_SISTEMA', 'Administrador del Sistema'),
        ('ADMIN_REGIONAL', 'Administrador Regional'),
        ('JEFE_DIVISION', 'Jefe de División'),
        ('ENCARGADO_OPERATIVO', 'Encargado Operativo'),
    ]
    divisiones = Division.query.filter_by(activo=True).order_by(Division.orden_jerarquico).all()

    return render_template('admin/usuarios/nuevo.html',
                           roles=roles_disponibles,
                           divisiones=divisiones)


@admin_bp.route('/usuarios/<uuid:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def usuarios_editar(id):
    """Editar usuario existente (AS-04)."""
    usuario = Usuario.query.get_or_404(id)

    if request.method == 'POST':
        # Actualizar persona
        usuario.persona.nombres = request.form.get('nombres', '').strip()
        usuario.persona.apellido_paterno = request.form.get('apellido_paterno', '').strip()
        usuario.persona.apellido_materno = request.form.get('apellido_materno', '').strip() or None
        usuario.persona.email = request.form.get('email', '').strip() or None
        usuario.persona.telefono = request.form.get('telefono', '').strip() or None
        usuario.persona.cargo = request.form.get('cargo', '').strip() or None

        # Actualizar usuario
        nuevo_username = request.form.get('username', '').strip()
        if nuevo_username != usuario.username:
            if Usuario.query.filter(Usuario.username == nuevo_username, Usuario.id != id).first():
                flash(f'Ya existe otro usuario con username {nuevo_username}.', 'error')
                return redirect(url_for('admin.usuarios_editar', id=id))
            usuario.username = nuevo_username

        usuario.rol_crisis = request.form.get('rol_crisis')

        db.session.commit()
        flash('Usuario actualizado correctamente.', 'success')
        return redirect(url_for('admin.usuarios_lista'))

    roles_disponibles = [
        ('ADMIN_SISTEMA', 'Administrador del Sistema'),
        ('ADMIN_REGIONAL', 'Administrador Regional'),
        ('JEFE_DIVISION', 'Jefe de División'),
        ('ENCARGADO_OPERATIVO', 'Encargado Operativo'),
    ]
    divisiones = Division.query.filter_by(activo=True).order_by(Division.orden_jerarquico).all()

    return render_template('admin/usuarios/editar.html',
                           usuario=usuario,
                           roles=roles_disponibles,
                           divisiones=divisiones)


@admin_bp.route('/usuarios/<uuid:id>/toggle-activo', methods=['POST'])
@login_required
@admin_required
def usuarios_toggle_activo(id):
    """Activar/Desactivar usuario (AS-05)."""
    usuario = Usuario.query.get_or_404(id)

    if usuario.id == current_user.id:
        flash('No puedes desactivar tu propio usuario.', 'error')
    else:
        usuario.activo = not usuario.activo
        db.session.commit()
        estado = 'activado' if usuario.activo else 'desactivado'
        flash(f'Usuario {usuario.username} {estado}.', 'success')

    return redirect(url_for('admin.usuarios_lista'))


@admin_bp.route('/usuarios/<uuid:id>/reset-password', methods=['POST'])
@login_required
@admin_required
def usuarios_reset_password(id):
    """Restablecer contraseña de usuario (AS-06)."""
    usuario = Usuario.query.get_or_404(id)
    # En desarrollo, simplemente notificamos
    # En producción: generar token, enviar email, etc.
    flash(f'Se enviaría email de restablecimiento a {usuario.persona.email or "sin email"}.', 'info')
    return redirect(url_for('admin.usuarios_editar', id=id))


# =============================================================================
# Gestión de Divisiones (AS-01, AS-02)
# =============================================================================

@admin_bp.route('/divisiones')
@login_required
@admin_required
def divisiones_lista():
    """Lista de divisiones del GORE."""
    divisiones = Division.query.order_by(Division.orden_jerarquico, Division.nombre).all()
    return render_template('admin/divisiones/lista.html', divisiones=divisiones)


@admin_bp.route('/divisiones/nueva', methods=['GET', 'POST'])
@login_required
@admin_required
def divisiones_nueva():
    """Crear nueva división (AS-01)."""
    if request.method == 'POST':
        codigo = request.form.get('codigo', '').strip().upper()
        nombre = request.form.get('nombre', '').strip()
        sigla = request.form.get('sigla', '').strip().upper() or None
        orden = request.form.get('orden_jerarquico', type=int) or 0

        if not all([codigo, nombre]):
            flash('Código y nombre son obligatorios.', 'error')
        elif Division.query.filter_by(codigo=codigo).first():
            flash(f'Ya existe una división con código {codigo}.', 'error')
        else:
            division = Division(
                codigo=codigo,
                nombre=nombre,
                sigla=sigla,
                orden_jerarquico=orden,
                activo=True
            )
            db.session.add(division)
            db.session.commit()
            flash(f'División {codigo} creada correctamente.', 'success')
            return redirect(url_for('admin.divisiones_lista'))

    return render_template('admin/divisiones/nueva.html')


@admin_bp.route('/divisiones/<uuid:id>/editar', methods=['GET', 'POST'])
@login_required
@admin_required
def divisiones_editar(id):
    """Editar división existente (AS-02)."""
    division = Division.query.get_or_404(id)

    if request.method == 'POST':
        nuevo_codigo = request.form.get('codigo', '').strip().upper()
        if nuevo_codigo != division.codigo:
            if Division.query.filter(Division.codigo == nuevo_codigo, Division.id != id).first():
                flash(f'Ya existe otra división con código {nuevo_codigo}.', 'error')
                return redirect(url_for('admin.divisiones_editar', id=id))
            division.codigo = nuevo_codigo

        division.nombre = request.form.get('nombre', '').strip()
        division.sigla = request.form.get('sigla', '').strip().upper() or None
        division.orden_jerarquico = request.form.get('orden_jerarquico', type=int) or 0
        division.activo = request.form.get('activo') == '1'

        db.session.commit()
        flash('División actualizada correctamente.', 'success')
        return redirect(url_for('admin.divisiones_lista'))

    return render_template('admin/divisiones/editar.html', division=division)
