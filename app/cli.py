# =============================================================================
# app/cli.py — Comandos CLI de Flask
# =============================================================================

import click
from flask.cli import with_appcontext
from app.extensions import db


@click.command('create-admin')
@click.option('--username', default='admin', help='Username del admin')
@with_appcontext
def create_admin(username):
    """Crear usuario administrador."""
    from app.models import Persona, Usuario
    import uuid

    # Verificar si ya existe
    existing = Usuario.query.filter_by(username=username).first()
    if existing:
        existing.rol_crisis = 'ADMIN_SISTEMA'
        existing.activo = True
        db.session.commit()
        click.echo(f'✓ Usuario {username} actualizado como ADMIN_SISTEMA')
        return

    # Crear persona
    persona = Persona(
        id=uuid.uuid4(),
        rut='11111111-1',
        nombres='Administrador',
        apellido_paterno='Sistema',
        apellido_materno='GORE',
        email='admin@gorenuble.cl'
    )
    db.session.add(persona)
    db.session.flush()  # Para obtener el ID

    # Crear usuario
    usuario = Usuario(
        id=uuid.uuid4(),
        persona_id=persona.id,
        username=username,
        activo=True,
        rol_crisis='ADMIN_SISTEMA'
    )
    db.session.add(usuario)

    db.session.commit()
    click.echo(f'✓ Usuario admin creado: {username} / admin123')


@click.command('create-test-users')
@with_appcontext
def create_test_users():
    """Crear usuarios de prueba para cada rol de crisis.

    Todos usan la contraseña de desarrollo: admin123
    """
    from app.models import Persona, Usuario
    import uuid

    # Definición de usuarios por rol
    test_users = [
        {
            'username': 'admin',
            'rut': '11111111-1',
            'nombres': 'Administrador',
            'apellido_paterno': 'Sistema',
            'apellido_materno': 'GORE',
            'email': 'admin@gorenuble.cl',
            'rol_crisis': 'ADMIN_SISTEMA',
        },
        {
            'username': 'aregional',
            'rut': '22222222-2',
            'nombres': 'Ana',
            'apellido_paterno': 'Regional',
            'apellido_materno': 'GORE',
            'email': 'aregional@gorenuble.cl',
            'rol_crisis': 'ADMIN_REGIONAL',
        },
        {
            'username': 'jefe_div',
            'rut': '33333333-3',
            'nombres': 'Juan',
            'apellido_paterno': 'Jefe',
            'apellido_materno': 'Division',
            'email': 'jefe.division@gorenuble.cl',
            'rol_crisis': 'JEFE_DIVISION',
        },
        {
            'username': 'encargado',
            'rut': '44444444-4',
            'nombres': 'Elena',
            'apellido_paterno': 'Encargada',
            'apellido_materno': 'Operativa',
            'email': 'encargado@gorenuble.cl',
            'rol_crisis': 'ENCARGADO_OPERATIVO',
        },
    ]

    for data in test_users:
        usuario = Usuario.query.filter_by(username=data['username']).first()
        if usuario:
            # Si ya existe, solo actualizamos rol y activamos
            usuario.rol_crisis = data['rol_crisis']
            usuario.activo = True
            click.echo(f'- Actualizado usuario existente: {data["username"]} ({data["rol_crisis"]})')
            continue

        # Verificar si hay persona con mismo RUT
        persona = Persona.query.filter_by(rut=data['rut']).first()
        if not persona:
            persona = Persona(
                id=uuid.uuid4(),
                rut=data['rut'],
                nombres=data['nombres'],
                apellido_paterno=data['apellido_paterno'],
                apellido_materno=data['apellido_materno'],
                email=data['email'],
                activo=True,
            )
            db.session.add(persona)
            db.session.flush()

        usuario = Usuario(
            id=uuid.uuid4(),
            persona_id=persona.id,
            username=data['username'],
            activo=True,
            rol_crisis=data['rol_crisis'],
        )
        db.session.add(usuario)
        click.echo(f'+ Creado usuario: {data["username"]} ({data["rol_crisis"]})')

    db.session.commit()
    click.echo('\nTodos los usuarios de prueba usan la contraseña: admin123')


@click.command('list-users')
@with_appcontext
def list_users():
    """Listar usuarios del sistema."""
    from app.models import Usuario

    usuarios = Usuario.query.all()
    if not usuarios:
        click.echo('No hay usuarios.')
        return

    click.echo(f'\n{"Username":<20} {"Nombre":<30} {"Rol":<20} {"Activo":<8}')
    click.echo('-' * 80)
    for u in usuarios:
        nombre = u.nombre_completo[:28] if u.nombre_completo else '-'
        click.echo(f'{u.username or "-":<20} {nombre:<30} {u.rol_crisis or "-":<20} {"Sí" if u.activo else "No":<8}')


def init_app(app):
    """Registrar comandos CLI."""
    app.cli.add_command(create_admin)
    app.cli.add_command(list_users)
    app.cli.add_command(create_test_users)
