from app import create_app, db
from app.models.actores import Persona, Usuario
import uuid

app = create_app()

with app.app_context():
    print("Seeding Admin User...")

    # 1. Ensure persona exists
    persona_rut = "11111111-1"
    persona = Persona.query.filter_by(rut=persona_rut).first()
    if not persona:
        persona = Persona(
            id=uuid.uuid4(),
            rut=persona_rut,
            nombres="Administrador",
            apellido_paterno="Sistema",
            apellido_materno="GORE",
            email="admin@gorenuble.cl",
        )
        db.session.add(persona)
        db.session.commit()
        print(f"Persona {persona.rut} created.")
    else:
        print(f"Persona {persona.rut} already exists.")

    # 2. Ensure usuario exists
    username = "admin"
    usuario = Usuario.query.filter_by(username=username).first()
    if not usuario:
        usuario = Usuario(
            persona_id=persona.id, username=username, rol_crisis="ADMIN_SISTEMA"
        )
        db.session.add(usuario)
        db.session.commit()
        print(f"Usuario {usuario.username} created.")
    else:
        usuario.rol_crisis = "ADMIN_SISTEMA"
        usuario.activo = True
        db.session.commit()
        print(f"Usuario {usuario.username} updated to ADMIN_SISTEMA.")

    print("DONE.")
